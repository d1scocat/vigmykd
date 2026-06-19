import pygame

import json
import logging

from pathlib import Path
from typing import Any

from auth.server import ServerAuthenticator
from config import Config
from event import EventManager
from i18n import Localization
from network import ApiClient
from textures import loader, TextureManager
from world import HeadlessWorld, World


class GameContext:
    def __init__(
        self,
        logger: logging.Logger,
        event_manager: EventManager,
        assets_path: Path,
        cfg_path: Path,
        cfg: Config,
        client: ApiClient,
        screen_size: tuple[int, int]
    ):
        self.logger = logger
        self.event_manager = event_manager
        self.screen_size = screen_size

        self.assets_path = assets_path
        self.cfg_path = cfg_path

        self.maps_path = assets_path / "maps"
        self.sheets_path = assets_path / "sheets"
        self.ui_path = assets_path / "ui"
        self.font_path = assets_path / "fonts"
        self.key_path = assets_path / "pubkey.pem"

        self.cfg = cfg
        self.localization = Localization(assets_path / "i18n", "en-US")

        self.font_sources = self._preload_fonts()
        self.font_cache: dict[tuple[str, int], pygame.font.Font] = {}

        self.api_client = client

        self.auth_path = cfg_path / "auth.dat"
        self.auth = ServerAuthenticator(client, self.auth_path)

        self.texture_manager = TextureManager()

        self._map_data = self._prefetch_maps()
        self.world_prefetch = self._preload_worlds()

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

    def _preload_fonts(self) -> dict[str, Path]:
        result = {}
        for file in self.font_path.iterdir():
            if file.is_dir():
                continue

            if file.suffix.lower() not in [".ttf", ".otf"]:
                continue

            name = file.stem
            result[name] = file
        return result

    def _prefetch_maps(self) -> dict[str, dict[str, Any]]:
        result = {}

        datas: list[Path] = []
        for file in self.maps_path.iterdir():
            if file.is_dir():
                mapdata = file / f"{file.name}.mapdata"
                if mapdata.is_file():
                    datas.append(mapdata)

        for data in datas:
            mapdata_json = json.loads(data.read_text())

            name = mapdata_json["name"]

            assets_dir = data.parent / mapdata_json["assets_directory"]

            result[name] = {
                "map_path": data.parent / mapdata_json["map_json"],
                "tileset_path": data.parent / mapdata_json["tileset_json"],
                "assets_dir": assets_dir,
                "spritesheet_image": assets_dir / mapdata_json["spritesheet_image"],
                "spritesheet_details": assets_dir / mapdata_json["spritesheet_details"],
            }

        return result

    def _preload_worlds(self) -> dict[str, World]:
        result = {}

        # setup a big enough starting point to not overlap
        # with any previous spritesheet definitions
        start = 10000

        for idx, (world_name, world_data) in enumerate(self._map_data.items()):
            sheet_id = start + idx
            sheet_data = loader.texture_packer_to_spritesheet(
                sheet_id=sheet_id,
                file=world_data["spritesheet_details"],
                spritesheet=world_data["spritesheet_image"]
            )

            loader.load_sheet(
                sheet=sheet_data,
                parent_path=world_data["assets_dir"],
                manager=self.texture_manager
            )

            _headless = HeadlessWorld(
                tmj_path=world_data["map_path"],
                tsj_path=world_data["tileset_path"]
            )

            result[world_name] = World(
                headless=_headless,
                texture_manager=self.texture_manager,
                sheet_id=sheet_id
            )

        return result


    def fetch_font(self, name: str, size: int) -> pygame.font.Font:
        key = (name, size)

        if key in self.font_cache:
            return self.font_cache[key]

        if name in self.font_sources:
            font = pygame.font.Font(str(self.font_sources[name]), size)
        else:
            self.logger.warning("Font '%s' not found, using fallback", {name})
            font = pygame.font.SysFont(None, size)

        self.font_cache[key] = font
        return font

    def fetch_map(self, name: str) -> dict[str, Any] | None:
        return self._map_data.get(name, None)
