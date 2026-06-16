from ui.components.component import UIComponent

from typing import Any


class UIContainer(UIComponent):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        texture: dict[str, Any] | None,
        children: list[UIComponent],
        states: dict[str, dict[str, Any]] | None = None,
        default_state: str | None = None,
    ):
        super().__init__(
            id=id,
            type="container",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state
        )

        self.texture = texture
        self.children = children
