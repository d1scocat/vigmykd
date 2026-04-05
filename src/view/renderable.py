from dataclasses import dataclass
from typing import Tuple


@dataclass
class RenderState:
    sheet_id: int
    grid_pos: Tuple[int, int]
    origin: Tuple[float, float]


@dataclass
class Renderable:
    states: dict[int, RenderState]
    current_state_id: int
    location: Tuple[int, int] = (0, 0)

# dev test
renderable_player = Renderable(
    {0: RenderState(
        sheet_id=1,
        grid_pos=(0, 0),
        origin=(0.5, 0.5)
    )},
    0,
    location=(200, 200)
)