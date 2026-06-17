import uuid

from typing import Any, Callable

from pygame.event import Event

from context import GameContext
from event.events import UDPReceivedEvent
from game.model import GameState
from network.udp.factory import Packets
from player import Facing, Player
from scene.objects.match import actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextElement
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

from generated.proto.v1 import packet_pb2 as packet_pb2


class MatchScene(Scene):
    def __init__(
        self,
        model: GameState,
        ctx: GameContext,
    ):
        from registry import registries
        self.input_router = registries.consumers.router_by_tag("match")

        self.model = model
        self.ctx = ctx

        self._ui_interaction = UIInteractionSystem()

        self._ui_page = self.get_ui(ctx.ui_path / "match.json")

        self.action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None] = {
        }

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def tick(self):
        super().default_tick(self.ctx, self.input_router)

    def render(self, view: Renderer, view_system: ViewSystem):
        view.drop_render_queue()

        self.page.process()
        self.page.resolve_layout(self.ctx.screen_size, self.ctx)
        self.page.submit_ui(view)

        view_system.update(self.model)
        view_system.submit(view)

    def on_load(self):
        actions.request_match_info(self.model)

    def on_enter(self):
        self.lids = [
            self.ctx.event_manager.register_listener(
                UDPReceivedEvent,
                self.piggyback_receiver
            ),

            self.ctx.event_manager.register_listener(
                UDPReceivedEvent,
                self.match_start_info_receiver
            )
        ]

    def on_exit(self):
        for lid in self.lids:
            self.ctx.event_manager.unregister_listener(lid)

    def match_start_info_receiver(self, event: UDPReceivedEvent):
        if event.message_type != packet_pb2.RequestMatchInfoResponse:
            return
        
        self.model.prepare_match(event.message.rng_seed, event.message.initial_server_tick)

        player1, player2 = list(event.message.players)
        try:
            client_id = uuid.UUID(event.message.your_id)

            player1_id = uuid.UUID(player1.uuid)
            player2_id = uuid.UUID(player2.uuid)

            player1 = Player.from_packet(player1, client_id == player1_id)
            player2 = Player.from_packet(player2, client_id == player2_id)

        except Exception:
            self.ctx.logger.exception("Could not create players when starting match")
            raise

        self.model.set_client_player(player1 if player1.is_client else player2)
        self.model.set_opponent_player(player2 if player1.is_client else player1)
        self.model.is_in_match = True

    def piggyback_receiver(self, event: UDPReceivedEvent):
        if event.message_type != packet_pb2.Reconcile:
            return

        server_tick: int = event.message.server_tick
        last_client_tick: int = event.message.last_client_tick
        players = list(event.message.players)

        self.model.reconcile(server_tick, last_client_tick, players, self.ctx)
        
    def find_action(self, action_name: str):
        return self.action_mapping.get(action_name, None)

    def on_event(self, event: Event) -> bool:
        return False
