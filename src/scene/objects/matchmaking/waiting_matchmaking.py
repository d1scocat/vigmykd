from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import HTTPResponseEvent, UDPReceivedEvent, UDPAckEvent, \
    SceneSwitchRequestEvent, PrepareSceneRequestEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.objects.kicked import KickedScene
from scene.objects.menu import MenuScene
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem

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

    def _prepare_matchmaking_scene(self):
        from scene.objects.matchmaking import MatchmakingScene

        self.matchmaking_scene = MatchmakingScene(self.model, self.ctx, '...')
        self.ctx.event_manager.invoke_event(PrepareSceneRequestEvent(self.matchmaking_scene))

    def _init_matchmaking_flow(self):
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

    def on_enter(self):
        self.lids.append(self.ctx.event_manager.register_listener(
            event_type=HTTPResponseEvent,
            func=self.match_register_listener
        ))

        self._prepare_matchmaking_scene()
        self._init_matchmaking_flow()

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
            ),  # register here to ensure existence of attr 'msg_id'

            self.ctx.event_manager.register_listener(
                event_type=UDPReceivedEvent,
                func=self.match_id_received_listener
            )
        ])

        self.msg_id = packet.msg_id

        self.model.server_client.enqueue(Packets.envelope(packet), self.msg_id, True)

    def queue_enter_listener(self, event: UDPAckEvent):
        if event.msg_id != self.msg_id:
            return
        if not event.ok:
            self._back_to_menu()
            return
        self.check_and_start_matchmaking()

    def udp_receiver(self, event: UDPReceivedEvent):
        if event.message_type == packet_pb2.MatchmakingEnterResponse:
            self.matchmaking_scene.match_id = event.message.match_id
            self.check_and_start_matchmaking()
            return

        if event.message_type == packet_pb2.KickedFromMatch:
            key = event.message.reason_i18n
            scene = KickedScene(self.model, self.ctx, key)

            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(scene))

    def check_and_start_matchmaking(self):
        self.ready_state += 1
        if self.ready_state == 2:
            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(self.matchmaking_scene))

    def on_load(self):
        pass

    def _back_to_menu(self):
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(
            self.model, self.ctx
        )))

    def on_event(self, event: Event) -> bool:
        return False
