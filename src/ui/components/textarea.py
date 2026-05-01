from ui.components.component import UIComponent

from typing import Any, Dict

class UITextArea(UIComponent):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        texture: Dict[str, Any] | None,
        label: Dict[str, Any],
        hint: Dict[str, Any],
    ):
        super().__init__(
            id=id,
            type="textarea",
            z_index=z_index,
            position=position,
            size=size,
        )

        self.texture = texture

        self.label = label
        self.hint = hint

        # runtime
        self.value: str = ""
        self.focused: bool = False