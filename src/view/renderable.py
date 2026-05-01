from dataclasses import dataclass
from typing import Tuple


@dataclass
class RenderState:
    sheet_id: int
    grid_pos: Tuple[int, int]
    origin: Tuple[float, float]


@dataclass
class Renderable:
    z_index: int
    states: dict[str, RenderState]
    current_state: str
    location: Tuple[int, int] = (0, 0)
