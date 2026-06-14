from typing import Any, Callable, Dict

from pygame.event import Event

from context import GameContext
from event.events import HTTPResponseEvent, SceneSwitchRequestEvent, UDPAckEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.objects.matchmaking import waiting_actions
from scene.objects.menu import MenuScene
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

from generated.proto.v1 import packet_pb2 as packet_pb2


class WaitingToMatchmake(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("matchmaking")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "waiting-to-matchmake.json")

        self.action_mapping: Dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {
            "quit": waiting_actions.quit_matchmaking
        }

        ctx.api_client.post(
            "/matchmaking/start",
            headers={"Authorization": f"Bearer {ctx.auth.get_token()}"}
        )

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
        self.mr_lid = self.ctx.event_manager.register_listener(
            event_type=HTTPResponseEvent,
            func=self.match_register_listener
        )

    def on_exit(self):
        if hasattr(self, "mr_lid"):
            self.ctx.event_manager.unregister_listener(self.mr_lid)
        if hasattr(self, "ms_lid"):
            self.ctx.event_manager.unregister_listener(self.ms_lid)

    def match_register_listener(self, event: HTTPResponseEvent):
        if event.endpoint != "/matchmaking/start":
            return
        if not event.success:
            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
                self.model, self.ctx
            )))
            return

        match_id = event.payload["match_id"]
        join_token = event.payload["join_token"]
        packet = Packets.matchmaking_enter(
            match_id=match_id,
            join_token=join_token
        )

        self.ms_lid = self.ctx.event_manager.register_listener(
            event_type=UDPAckEvent,
            func=self.match_start_listener
        )

        self.msg_id = packet.msg_id

        self.model.server_client.enqueue(Packets.envelope(packet), self.msg_id)

    def match_start_listener(self, event: UDPAckEvent):
        if event.msg_id != self.msg_id:
            return
        if event.ok:
            # or it will scream at me for circular imports etc!
            # ...probably
            from scene.objects.matchmaking import Matchmaking

            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(Matchmaking(
                self.model, self.ctx
            )))

    def find_action(self, action_name: str):
        return None

    def on_event(self, event: Event) -> bool:
        return False
