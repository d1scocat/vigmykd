from pathlib import Path
import logging

from auth import MockAuthenticator
from config import load_config
from event import EventManager
from textures import TextureManager
from registry import GlobalRegistries, registries as reg_sngltn


class GameContext:
    registries: GlobalRegistries

    def init_registries(self):
        self.registries = reg_sngltn

        for registry in self.registries:
            registry.discover()
            registry.init_all()

    def __init__(self, assets_path: Path):
        self.event_manager = EventManager()
        self.assets_path = assets_path

        self.cfg = load_config(assets_path / "config.json")

        self.auth_path = assets_path / "auth.dat"
        self.auth = MockAuthenticator(self.auth_path)
        if not self.auth_path.exists():
            self.auth.login(None)

        self.logger = logging.getLogger("vigmykd")

        self.texture_manager = TextureManager()

        self.init_registries()
