import json

from logging import Logger
from pathlib import Path

from typing import Any, Dict, get_type_hints, get_origin


class GameServerConfig:
    _subpath = "sock.json"

    port: int
    scan_for_max: int
    server_addr: str
    server_port: int

    def __init__(self, logger: Logger, cfg_path: Path):
        self._schema = get_type_hints(self.__class__)

        self.logger = logger

        sock_cfg = json.loads((cfg_path / self._subpath).read_text())

        try:
            self._dump(sock_cfg)
        except Exception:
            self.logger.error("Malformed socket configuration", exc_info=True)
            raise

    def _dump(self, cfg: Dict[str, Any], prefix = ""):
        for key, value in cfg.items():
            name = f"{prefix}{key}"

            if isinstance(value, dict):
                self._dump(value, f"{name}_")
                continue

            if name not in self._schema:
                raise KeyError(f"Unexpected socket config field: {name}")

            expected = self._schema[name]
            origin = get_origin(expected) or expected
            if not isinstance(value, origin):
                raise TypeError(f"{name} expected {origin}, got {type(value)}")

            setattr(self, name, value)
