from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import HTTPResponseEvent, SceneSwitchRequestEvent, UDPAckEvent, UDPReceivedEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.objects.menu import MenuScene
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

from generated.proto.v1 import packet_pb2 as packet_pb2


class WaitingToMatchmakeScene(Scene):
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

        self.action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {
        }

        self.ready_state = 0
        self.match_id: str
        self.lids = []

        self.init_matchmaking_flow()

    def init_matchmaking_flow(self):
        self.ctx.api_client.post(
            "/matchmaking/start",
            headers={"Authorization": f"Bearer {self.ctx.auth.get_token()}"}
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
        self.lids.append(self.ctx.event_manager.register_listener(
            event_type=HTTPResponseEvent,
            func=self.match_register_listener
        ))

    def on_exit(self):
        for lid in self.lids:
            self.ctx.event_manager.unregister_listener(lid)

    def match_register_listener(self, event: HTTPResponseEvent):
        if event.endpoint != "/matchmaking/start":
            return
        if not event.success:
            self._back_to_menu()
            return

        match_id = event.payload["match_id"]
        join_token = event.payload["join_token"]
        packet = Packets.matchmaking_enter(
            match_id=match_id,
            join_token=join_token
        )

        self.lids.extend([
            self.ctx.event_manager.register_listener(
                event_type=UDPAckEvent,
                func=self.queue_enter_listener
            ),

            self.ctx.event_manager.register_listener(
                event_type=UDPReceivedEvent,
                func=self.match_id_received_listener
            )
        ])

        self.msg_id = packet.msg_id

        self.model.server_client.enqueue(Packets.envelope(packet), self.msg_id)

    def queue_enter_listener(self, event: UDPAckEvent):
        if event.msg_id != self.msg_id:
            return
        if not event.ok:
            self._back_to_menu()
            return
        self.check_and_start_matchmaking()

    def match_id_received_listener(self, event: UDPReceivedEvent):
        if event.message_type != packet_pb2.MatchmakingEnterResponse:
            return
        self.match_id = event.message.match_id
        self.check_and_start_matchmaking()

    def check_and_start_matchmaking(self):
        self.ready_state += 1
        if self.ready_state == 2:
            # or it will scream at me for circular imports etc!
            # ...probably
            from scene.objects.matchmaking import MatchmakingScene

            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MatchmakingScene(
                self.model, self.ctx, self.match_id
            )))

    def _back_to_menu(self):
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
            self.model, self.ctx
        )))

    def find_action(self, action_name: str):
        return None

    def on_event(self, event: Event) -> bool:
        return False
