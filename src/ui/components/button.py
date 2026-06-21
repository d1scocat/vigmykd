from ui.components.component import UIComponent
from ui.components.text import UIText, UITextHolder

from typing import Any


class UIButton(UIComponent, UITextHolder):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        states: dict[str, dict[str, Any]],
        action: str,
        texture: dict[str, Any] | None,
        text: dict[str, Any] | None = None,
        default_state: str | None = None,
        is_hud: bool = False,
    ):
        super().__init__(
            id=id,
            type="button",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state,
            is_hud=is_hud
        )

        self.texture = texture

        self.action = action

        self.text_obj = None
        if text is not None:
            self.text_obj = UIText(
                raw=text.get("raw", None),
                i18n=text.get("i18n", None),
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
