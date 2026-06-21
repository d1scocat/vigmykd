import settings

from ui.components.component import UIComponent
from ui.components.text import UIText, UITextHolder
from view.renderer import Renderer

from typing import Any

import pygame


class UITextArea(UIComponent, UITextHolder):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        texture: dict[str, Any] | None,
        label: dict[str, Any],
        hint: dict[str, Any],
        default_state: str | None = None,
        states: dict[str, dict[str, Any]] | None = None,
        password_mode: bool = False,
        is_hud: bool = False,
    ):
        super().__init__(
            id=id,
            type="textarea",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state,
            is_hud=is_hud
        )

        self.texture = texture

        self.label = label
        self.hint = hint

        self.password_mode = password_mode

        self.value: str = ""

        self.cursor = 0

        self._repeat_timers: dict[str, Any | None] = {}

        self._actions = {
            "backspace": self.delete_char,
            "delete": self.delete_next_char,
            "ctrl_backspace": self.delete_word,
            "ctrl_delete": self.delete_next_word,
            "left": lambda: self.move_cursor(-1),
            "right": lambda: self.move_cursor(1),
            "ctrl_left": lambda: self.move_cursor_word(-1),
            "ctrl_right": lambda: self.move_cursor_word(1),
        }

    @property
    def text(self) -> UIText:
        if not self.value:
            return UIText(
                raw=self.hint.get("raw"),
                i18n=self.hint.get("i18n"),
                font=self.hint["font"],
                size=self.hint["size"],
                color=self.hint["color"],
            )

        if self.password_mode:
            return UIText(
                raw="*" * len(self.value),
                i18n=None,
                font=self.label["font"],
                size=self.label["size"],
                color=self.label["color"],
            )

        return UIText(
            raw=self.value,
            i18n=None,
            font=self.label["font"],
            size=self.label["size"],
            color=self.label["color"],
        )

    def _update_timer_handle(
        self,
        keys: pygame.key.ScancodeWrapper,
        key: int,
        mods: int,
        value: str
    ):
        if keys[key]:
            if mods & pygame.KMOD_CTRL:
                self._handle_repeat(f"ctrl_{value}")
            else:
                self._handle_repeat(value)
        else:
            self._repeat_timers[value] = None
            self._repeat_timers[f"ctrl_{value}"] = None

    def update(self, keys: pygame.key.ScancodeWrapper):
        if not self.focused:
            return

        mods = pygame.key.get_mods()

        self._update_timer_handle(keys, pygame.K_BACKSPACE, mods, "backspace")
        self._update_timer_handle(keys, pygame.K_LEFT, mods, "left")
        self._update_timer_handle(keys, pygame.K_RIGHT, mods, "right")
        self._update_timer_handle(keys, pygame.K_DELETE, mods, "delete")

    def _trigger(self, key: str):
        action = self._actions.get(key)
        if action:
            action()

    def _handle_repeat(self, key: str):
        now = pygame.time.get_ticks()
        state = self._repeat_timers.get(key)

        if state is None:
            self._trigger(key)

            self._repeat_timers[key] = {
                "start": now,
                "last": now,
                "repeating": False
            }
            return

        if not state["repeating"]:
            if now - state["start"] >= settings.TEXT_INPUT_HOLD_DELAY:
                state["repeating"] = True
                state["last"] = now
                self._trigger(key)
        else:
            if now - state["last"] >= settings.TEXT_INPUT_HOLD_INTERVAL:
                state["last"] = now
                self._trigger(key)

    def move_cursor(self, delta: int):
        self.cursor = max(0, min(len(self.value), self.cursor + delta))

    def move_cursor_word(self, direction: int):
        if direction < 0:
            i = self.cursor - 1
            while i > 0 and self.value[i].isspace():
                i -= 1
            while i > 0 and not self.value[i].isspace():
                i -= 1
            self.cursor = i
        else:
            i = self.cursor
            n = len(self.value)
            while i < n and not self.value[i].isspace():
                i += 1
            while i < n and self.value[i].isspace():
                i += 1
            self.cursor = i

    def calculate_cursor(self, renderer: Renderer) -> tuple[int, int, int, int] | None:
        if not self.focused:
            return None

        text = self.text
        font = renderer.ctx.fetch_font(text.font, text.size)

        content = renderer.ctx.ui_i18n(text, strict=False)
        display = content or ""

        before = display[:self.cursor]

        text_w, text_h = font.size(before)

        x, y = self.absolute_position
        w, h = self.absolute_size

        # make this configurable later in the text object itself
        padding_left = settings.PADDING_LEFT
        cursor_x = int(x + padding_left + text_w)
        cursor_y = int(y + (h - text_h) / 2)
        cursor_h = text_h

        return (cursor_x, cursor_y, settings.TEXT_CURSOR_WIDTH, cursor_h)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False

        mods = pygame.key.get_mods()

        if mods & pygame.KMOD_CTRL:
            if event.key == pygame.K_a:
                self.move_cursor(len(self.value) - self.cursor)
                return True

            if event.key == pygame.K_c:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.value.encode())
                return True

            if event.key == pygame.K_v:
                clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                if clipboard:
                    self.insert(clipboard
                                .decode()
                                .replace("\x00", "")
                                .replace("\n", " ")
                                .replace("\t", " ")
                                )
                return True

        if event.unicode and event.unicode.isprintable():
            self.insert(event.unicode)
            return True

        return False

    def insert(self, text: str):
        self.value = self.value[:self.cursor] + text + self.value[self.cursor:]
        self.cursor += len(text)

    def delete_char(self):
        if self.cursor > 0:
            self.value = self.value[:self.cursor - 1] + self.value[self.cursor:]
            self.cursor -= 1

    def delete_next_char(self):
        if self.cursor < len(self.value):
            self.value = self.value[:self.cursor] + self.value[self.cursor + 1:]

    def delete_word(self):
        if self.cursor == 0:
            return

        i = self.cursor - 1
        while i > 0 and self.value[i].isspace():
            i -= 1
        while i > 0 and not self.value[i].isspace():
            i -= 1

        self.value = self.value[:i] + self.value[self.cursor:]
        self.cursor = i

    def delete_next_word(self):
        if self.cursor >= len(self.value):
            return

        i = self.cursor
        while i < len(self.value) and self.value[i].isspace():
            i += 1
        while i < len(self.value) and not self.value[i].isspace():
            i += 1

        self.value = self.value[:self.cursor] + self.value[i:]
