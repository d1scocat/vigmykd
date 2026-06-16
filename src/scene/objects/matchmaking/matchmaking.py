from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import UDPReceivedEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.objects.matchmaking import matchmaking_actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextElement
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

from generated.proto.v1 import packet_pb2 as packet_pb2


class MatchmakingScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
        match_id: str
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("matchmaking")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "matchmaking.json")

        self.action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {
            "quit": waiting_actions.quit_matchmaking
        }

        self.match_id = match_id

        id_box = self.page.by_id("match-id-textbox")
        if id_box is None or not isinstance(id_box, UITextElement):
            self.ctx.logger.warning("No 'match-id-textbox' available for MatchmakingScene")
            return
        id_box.set_raw(match_id)

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
        self.lid = self.ctx.event_manager.register_listener(
            UDPReceivedEvent,
            self.match_start_listener
        )

    def on_exit(self):
        if hasattr(self, "lid"):
            self.ctx.event_manager.unregister_listener(self.lid)

    def match_start_listener(self, event: UDPReceivedEvent):
        if event.message_type != packet_pb2.InformMatchStart:
            return
        id_box = self.page.by_id("match-id-textbox")
        if id_box is None or not isinstance(id_box, UITextElement):
            self.ctx.logger.warning("No 'match-id-textbox' available for MatchmakingScene")
            return
        id_box.set_raw(f"{self.match_id} (started)")
        id_box.set_font_size(id_box.text_obj.size // 2)
        
    def find_action(self, action_name: str):
        return None

    def on_event(self, event: Event) -> bool:
        return False
