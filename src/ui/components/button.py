from typing import Callable, Optional, Self, Tuple


class Button:
    x: int
    y: int
    size_x: int
    size_y: int
    label: str
    on_click: Callable[[Self], None]

    design_tile_sheet_id: Optional[int]
    design_tile_id: Optional[int]

    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        label: str,
        on_click: Callable[[Self], None],
        design_tile_sheet_id: Optional[int] = None,
        design_tile_id: Optional[int] = None,
    ) -> None:
        self.x, self.y = pos
        self.size_x, self.size_y = size
        self.label = label
        self.on_click = on_click

        self.design_tile_sheet_id = design_tile_sheet_id
        self.design_tile_id = design_tile_id
