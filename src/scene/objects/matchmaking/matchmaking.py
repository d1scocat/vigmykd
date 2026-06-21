from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import UDPReceivedEvent, SceneSwitchRequestEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.objects.kicked import KickedScene
from scene.objects.match import MatchScene
from scene.objects.matchmaking import matchmaking_actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextElement
from ui.interaction import UIInteractionSystem

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

        self.action_mapping = {
            "quit": matchmaking_actions.quit_matchmaking
        }

        self._match_id = match_id

    @property
    def match_id(self):
        return self._match_id

    @match_id.setter
    def match_id(self, value: str):
        self._match_id = value

        id_box = self.page.by_id("match-id-textbox")
        if id_box is None or not isinstance(id_box, UITextElement):
            self.ctx.logger.warning("No 'match-id-textbox' available for MatchmakingScene")
            return
        id_box.set_raw(value)

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def on_load(self):
        self.lid = self.ctx.event_manager.register_listener(
            UDPReceivedEvent,
            self.udp_receiver
        )

    def on_enter(self):
        pass

    def on_exit(self):
        if hasattr(self, "lid"):
            self.ctx.event_manager.unregister_listener(self.lid)

    def udp_receiver(self, event: UDPReceivedEvent):
        if event.message_type == packet_pb2.KickedFromMatch:
            key = event.message.reason_i18n
            scene = KickedScene(self.model, self.ctx, key)

            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(scene))

            return

        if event.message_type != packet_pb2.InformMatchStart:
            return
        
        ack_packet = Packets.ack(event.envelope.packet.msg_id, True)
        self.model.server_client.enqueue(Packets.envelope(ack_packet), ack_packet.msg_id)

        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MatchScene(
            self.model, self.ctx
        )))

    def on_event(self, event: Event) -> bool:
        return False
