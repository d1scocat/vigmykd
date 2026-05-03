from ui.components.component import UIComponent
from ui.components.text import UIText, UITextHolder

from typing import Any, Dict


class UIButton(UIComponent, UITextHolder):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        states: Dict[str, Dict[str, Any]],
        action: str,
        text: Dict[str, Any] | None = None,
        default_state: str | None = None,
    ):
        super().__init__(
            id=id,
            type="button",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state
        )

        self.action = action

        self.text_obj = None
        if text is not None:
            self.text_obj = UIText(
                i18n=text["i18n"],
                font=text["font"],
                size=text["size"],
                color=tuple(text["color"])
            )

        self.hovered = False
        self.pressed = False

        self.current_state = "normal"

    @property
    def text(self) -> UIText | None:
        return self.text_obj
