from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import SceneSwitchRequestEvent
from game.model import GameState
from scene.objects.menu import MenuScene
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextElement
from ui.interaction import UIInteractionSystem

from generated.proto.v1 import packet_pb2 as packet_pb2


class KickedScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
        reason_key: str,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("kicked-from-match")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "kicked-from-match.json")

        self.action_mapping = {
            "quit": self._back_to_menu
        }

        self.reason_key = reason_key

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def on_load(self):
        pass

    def on_enter(self):
        reason_text = self.page.by_id("kick-reason")
        if reason_text is None or not isinstance(reason_text, UITextElement):
            self.ctx.logger.warning("No 'kick-reason' available for KickedScene")
            return
        reason_text.set_i18n(self.reason_key)

    def on_exit(self):
        pass

    def on_event(self, event: Event) -> bool:
        return False

    def _back_to_menu(self, _, __, ___):
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
            self.model, self.ctx
        )))
