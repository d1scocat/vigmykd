from abc import ABC, abstractmethod
from typing import Any

from ui.components.component import UIComponent


class UIText:
    def __init__(
        self,
        i18n: str | None,
        raw: str | None,
        font: str,
        size: int,
        color: tuple[int, int, int]
    ):
        if not i18n and not raw:
            raise ValueError("i18n and raw can't be None at the same time:"
                             f"{i18n=} | {raw=}")

        if i18n and raw:
            raise ValueError("i18n and raw can't be filled at the same time:"
                             f"{i18n=} | {raw=}")

        self.i18n = i18n
        self.raw = raw
        self.font = font
        self.size = size
        self.color = color


class UITextHolder(ABC):
    @property
    @abstractmethod
    def text(self) -> UIText | None:
        pass


class UITextElement(UIComponent, UITextHolder):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        text: dict[str, Any],
        states: dict[str, dict[str, Any]] | None = None,
        default_state: str | None = None,
        is_hud: bool = False,
    ):
        super().__init__(
            id=id,
            type="text",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state,
            is_hud=is_hud
        )

        self.text_obj = UIText(
            raw=text.get("raw", None),
            i18n=text.get("i18n", None),
            font=text["font"],
            size=text["size"],
            color=tuple(text["color"])
        )

        self.resolved_text_key = ""
        self.resolved_text_content = ""
        self.resolved_color = (0, 0, 0)
        self.resolved_font = ""
        self.resolved_font_size = self.text_obj.size

    def set_raw(self, raw: str):
        self.text_obj.raw = raw
        self.text_obj.i18n = None

    def set_i18n(self, key: str):
        self.text_obj.i18n = key
        self.text_obj.raw = None

    def set_font_size(self, size: int):
        self.text_obj.size = size

    def process_component(self):
        super().process_component()

        state = self.resolve_state()
        override = self.states.get(state, {})
        base = self.text_obj

        self.resolved_text_key = base.raw or base.i18n
        if override.get("text"):
            t = override["text"]
            self.resolved_text_key = t.get("raw") or t.get("i18n", self.resolved_text_key)

        self.resolved_color = tuple(override["color"]) if "color" in override else base.color
        self.resolved_font = override["font"] if "font" in override else base.font
        self.resolved_font_size = override["size"] if "size" in override else base.size

    @property
    def text(self) -> UIText:
        return self.text_obj
