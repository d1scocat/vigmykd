import uuid

from pygame.event import Event

from context import GameContext
from event.events import SceneSwitchRequestEvent, UDPReceivedEvent
from game.model import GameState
from player import Player
from scene.objects.kicked import KickedScene
from scene.objects.match import actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.components.text import UITextHolder
from ui.interaction import UIInteractionSystem

from generated.proto.v1 import packet_pb2 as packet_pb2

from settings import MAX_MANA, MAX_HEALTH


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

        self.action_mapping = {}

    @property
    def page(self) -> UIPage:
        return self._ui_page

    @property
    def interaction(self) -> UIInteractionSystem:
        return self._ui_interaction

    def on_load(self):
        actions.request_match_info(self.model)

    def tick(self):
        super().tick()

        client = self.model.client_player
        if client:
            client.mana = min(MAX_MANA, client.mana + 1)

            mana_textbox = self.page.by_id("mana-rectangle")
            if mana_textbox is None or not isinstance(mana_textbox, UITextHolder):
                self.ctx.logger.warning("No mana-rectangle found for MatchScene")
            else:
                mana_word = self.ctx.i18n("match.mana")
                mana_textbox.text.raw = f"{mana_word} | {client.mana} / {MAX_MANA}"
            
            hp_textbox = self.page.by_id("hp-rectangle")
            if hp_textbox is None or not isinstance(hp_textbox, UITextHolder):
                self.ctx.logger.warning("No hp-rectangle found for MatchScene")
            else:
                hp_word = self.ctx.i18n("match.hp")
                hp_textbox.text.raw = f"{hp_word} | {client.health:.0f} / {MAX_HEALTH:.0f}"

    def on_enter(self):
        self.lids = [
            self.ctx.event_manager.register_listener(
                UDPReceivedEvent,
                self.piggyback_receiver
            ),

            self.ctx.event_manager.register_listener(
                UDPReceivedEvent,
                self.udp_receiver
            )
        ]

    def on_exit(self):
        for lid in self.lids:
            self.ctx.event_manager.unregister_listener(lid)

    def udp_receiver(self, event: UDPReceivedEvent):
        if event.message_type == packet_pb2.KickedFromMatch:
            key = event.message.reason_i18n
            scene = KickedScene(self.model, self.ctx, key)

            self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(scene))

            return

        if event.message_type != packet_pb2.RequestMatchInfoResponse:
            return

        map_name = event.message.map_name
        self.set_world(self.ctx.world_prefetch.get(map_name))

        if not self.world:
            raise ValueError(f"Could not find and load map {map_name}")
        
        self.model.prepare_match(
            event.message.rng_seed,
            event.message.initial_server_tick,
            self.world
        )

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

    def on_event(self, event: Event) -> bool:
        return False
