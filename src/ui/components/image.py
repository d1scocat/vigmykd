from ui.components.component import UIComponent

from typing import Any


class UIImage(UIComponent):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        texture: dict[str, Any] | None,
        default_state: str | None = None,
        is_hud: bool = False,
    ):
        super().__init__(
            id=id,
            type="image",
            z_index=z_index,
            position=position,
            size=size,
            default_state=default_state,
            is_hud=is_hud
        )

        self.texture = texture
