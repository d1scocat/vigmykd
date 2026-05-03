from pathlib import Path
from typing import Dict, Tuple
from uuid import UUID

import logging

import pygame

from auth.mock import MockAuthenticator
from config import load_config
from event import EventManager
from i18n import Localization
from textures import TextureManager


class GameContext:
    def __init__(
        self,
        assets_path: Path,
        cfg_path: Path,
        screen_size: Tuple[int, int]
    ):
        self.event_manager = EventManager()

        self.assets_path = assets_path
        self.cfg_path = cfg_path

        self.sheets_path = assets_path / "sheets"
        self.ui_path = assets_path / "ui"
        self.font_path = assets_path / "fonts"

        self.screen_size = screen_size

        self.cfg = load_config(cfg_path / "config.json")
        self.localization = Localization(assets_path / "i18n", "en-US")

        self.font_sources = self._preload_fonts()
        self.font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}

        self.auth_path = cfg_path / "auth.dat"
        self.auth = MockAuthenticator(self.auth_path)
        if not self.auth_path.exists():
            self.auth.login(None)

        self.logger = logging.getLogger("vigmykd")

        self.texture_manager = TextureManager()

        self.local_player_id: UUID | None = self.auth.get_current_user(None)

    def i18n(self, key: str, strict: bool = False, **kwargs) -> str:
        """
        Resolve a localized string using the current context locale.

        Convenience wrapper around `Localization.t`, using the locale
        defined in this context's configuration.

        Args:
            key: Flattened translation key (e.g. "main-menu.login-button-label").
            strict: If True, do not fall back to the default locale.
            **kwargs: Values used to format the string.

        Returns:
            The formatted localized string for the active locale.
        """
        return self.localization.t(self.cfg.locale, key, strict, **kwargs)

    def _preload_fonts(self) -> Dict[str, Path]:
        result = {}
        for file in self.font_path.iterdir():
            if not file.is_dir():
                continue

            if file.suffix.lower() not in [".ttf", ".otf"]:
                continue

            name = file.stem
            result[name] = file
        return result

    def fetch_font(self, name: str, size: int) -> pygame.font.Font:
        key = (name, size)

        if key in self.font_cache:
            return self.font_cache[key]

        if name in self.font_sources:
            font = pygame.font.Font(str(self.font_sources[name]), size)
        else:
            self.logger.warning(f"Font '{name}' not found, using fallback")
            font = pygame.font.SysFont(None, size)

        self.font_cache[key] = font
        return font
