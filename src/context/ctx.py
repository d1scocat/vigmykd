from event import EventManager
from pathlib import Path
from config import Config, load_config

import logging
from logging import Logger


class GameContext:
    cfg: Config
    event_manager: EventManager
    assets_path: Path
    logger: Logger

    def __init__(self, assets_path: Path):
        self.event_manager = EventManager()
        self.assets_path = assets_path

        self.cfg = load_config(assets_path / "config.json")

        self.logger = logging.getLogger("vigmykd")
