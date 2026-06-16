import json
from pathlib import Path
from typing import FrozenSet
from dataclasses import dataclass

from config.loader import keymap_loader


@dataclass
class Config:
    keymap: dict[FrozenSet[int], str]

    locale: str
    server: str


def load_config(path: Path) -> Config:
    with open(path, "r") as cfg_file:
        data = json.load(cfg_file)

    keymap = keymap_loader.load_keymap(data["keymap"])

    return Config(
        keymap=keymap,

        locale=data["locale"],
        server=data["server"]
    )
