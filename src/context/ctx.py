from event import EventManager
from pathlib import Path
from config import load_config

import logging

from textures import TextureManager


class GameContext:
    def __init__(self, assets_path: Path):
        self.event_manager = EventManager()
        self.assets_path = assets_path

        self.cfg = load_config(assets_path / "config.json")

        self.logger = logging.getLogger("vigmykd")

        self.texture_manager = TextureManager()
