from pygame.event import Event

from context import GameContext
from event.events import SceneSwitchRequestEvent
from game.model import GameState
from scene.objects.menu import MenuScene
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem


class WonScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("won")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "won.json")

        self.action_mapping = {
            "quit": self._back_to_menu
        }

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def on_load(self):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_event(self, event: Event) -> bool:
        return False

    def _back_to_menu(self, _, __, ___):
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
            self.model, self.ctx
        )))
