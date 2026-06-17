from dataclasses import dataclass


@dataclass
class RenderState:
    sheet_id: int
    grid_pos: tuple[int, int]


@dataclass
class Renderable:
    z_index: int
    states: dict[str, RenderState]
    current_state: str
    location: tuple[float, float]
    size: tuple[int, int]
