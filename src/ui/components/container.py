from ui.components.component import UIComponent

from typing import Any, Dict, List

class UIContainer(UIComponent):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        texture: Dict[str, Any] | None,
        children: List["UIComponent"],
        states: Dict[str, Dict[str, Any]] | None = None,
    ):
        super().__init__(
            id=id,
            type="container",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
        )

        self.texture = texture
        self.children = children

        self.current_state = "shown"
