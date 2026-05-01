from ui.components.component import UIComponent

from typing import Any, Dict


class UIImage(UIComponent):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        texture: Dict[str, Any] | None,
    ):
        super().__init__(id, "image", z_index, position, size)

        self.texture = texture
