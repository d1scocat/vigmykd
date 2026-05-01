from pathlib import Path
from typing import Tuple
from uuid import UUID

import logging

from auth.mock import MockAuthenticator
from config import load_config
from event import EventManager
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

        self.screen_size = screen_size

        self.cfg = load_config(cfg_path / "config.json")

        self.auth_path = cfg_path / "auth.dat"
        self.auth = MockAuthenticator(self.auth_path)
        if not self.auth_path.exists():
            self.auth.login(None)

        self.logger = logging.getLogger("vigmykd")

        self.texture_manager = TextureManager()

        self.local_player_id: UUID | None = self.auth.get_current_user(None)
