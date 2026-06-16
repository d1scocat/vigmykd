from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from game.model import GameState
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem


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

        self.action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {}

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def tick(self):
        pass

    def render(self, view: Renderer, view_system: ViewSystem):
        view.drop_render_queue()

        self.page.process()
        self.page.resolve_layout(self.ctx.screen_size, self.ctx)
        self.page.submit_ui(view)

        view_system.update(self.model)
        view_system.submit(view)

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_load(self):
        pass

    def find_action(self, action_name: str):
        return None

    def on_event(self, event: Event) -> bool:
        return False
