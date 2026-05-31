from pathlib import Path
from typing import Dict, Tuple

import logging

import pygame

from auth.server import ServerAuthenticator
from config import Config
from event import EventManager
from i18n import Localization
from network import ApiClient
from textures import TextureManager


class GameContext:
    def __init__(
        self,
        logger: logging.Logger,
        event_manager: EventManager,
        assets_path: Path,
        cfg_path: Path,
        cfg: Config,
        client: ApiClient,
        screen_size: Tuple[int, int]
    ):
        self.logger = logger
        self.event_manager = event_manager
        self.screen_size = screen_size

        self.assets_path = assets_path
        self.cfg_path = cfg_path

        self.sheets_path = assets_path / "sheets"
        self.ui_path = assets_path / "ui"
        self.font_path = assets_path / "fonts"
        self.key_path = assets_path / "pubkey.pem"

        self.cfg = cfg
        self.localization = Localization(assets_path / "i18n", "en-US")

        self.font_sources = self._preload_fonts()
        self.font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}

        self.auth_path = cfg_path / "auth.dat"
        self.auth = ServerAuthenticator(client, self.auth_path)

        self.texture_manager = TextureManager()

    @property
    def local_player_id(self):
        return self.auth.get_user_id()

    def set_key(self, key: str):
        self.key_path.write_text(key)
        self.auth._set_key(key)

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
    
    def ui_i18n(self, text: "ui.components.text.UIText", strict: bool = False, **kwargs) -> str:
        """
        Resolve a localized string using the current context locale.

        Convenience wrapper around `Localization.t`, using the locale
        defined in this context's configuration.

        Args:
            text: The text object - may contain a i18n key or raw content.
            strict: If True, do not fall back to the default locale.
            **kwargs: Values used to format the string.

        Returns:
            The formatted localized string for the active locale.
        """
        if text.raw is not None:
            return format(text.raw, **kwargs)

        if text.i18n is None:
            raise ValueError("Text object doesn't contain i18n or raw content")

        return self.localization.t(self.cfg.locale, text.i18n, strict, **kwargs)

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
