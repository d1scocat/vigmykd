import settings

from ui.components.component import UIComponent
from ui.components.text import UIText, UITextHolder
from view.renderer import Renderer

from typing import Any, Dict, Tuple

import pygame


class UITextArea(UIComponent, UITextHolder):
    def __init__(
        self,
        id: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        texture: Dict[str, Any] | None,
        label: Dict[str, Any],
        hint: Dict[str, Any],
        default_state: str | None = None,
        states: Dict[str, Dict[str, Any]] | None = None,
        password_mode: bool = False
    ):
        super().__init__(
            id=id,
            type="textarea",
            z_index=z_index,
            position=position,
            size=size,
            states=states,
            default_state=default_state
        )

        self.texture = texture

        self.label = label
        self.hint = hint

        self.password_mode = password_mode

        self.value: str = ""

        self.cursor = 0

        self._repeat_timers: Dict[str, Any | None] = {}

        self._actions = {
            "backspace": self.delete_char,
            "ctrl_backspace": self.delete_word,
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
    
    def update(self, keys: pygame.key.ScancodeWrapper):
        if not self.focused:
            return

        mods = pygame.key.get_mods()

        if keys[pygame.K_BACKSPACE]:
            if mods & pygame.KMOD_CTRL:
                self._handle_repeat("ctrl_backspace")
            else:
                self._handle_repeat("backspace")
        else:
            self._repeat_timers["backspace"] = None
            self._repeat_timers["ctrl_backspace"] = None
        
        if keys[pygame.K_LEFT]:
            if mods & pygame.KMOD_CTRL:
                self._handle_repeat("ctrl_left")
            else:
                self._handle_repeat("left")
        else:
            self._repeat_timers["left"] = None
            self._repeat_timers["ctrl_left"] = None

        if keys[pygame.K_RIGHT]:
            if mods & pygame.KMOD_CTRL:
                self._handle_repeat("ctrl_right")
            else:
                self._handle_repeat("right")
        else:
            self._repeat_timers["right"] = None
            self._repeat_timers["ctrl_right"] = None
    
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
    
    def calculate_cursor(self, renderer: Renderer) -> Tuple[int, int, int, int] | None:
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

        padding_left = settings.PADDING_LEFT  # make this configurable later in the text object itself
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