from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from game.model import GameState
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem


class LimboScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "limbo.json")

        self.action_mapping = {}

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_load(self):
        pass

    def on_event(self, event: Event) -> bool:
        return False
