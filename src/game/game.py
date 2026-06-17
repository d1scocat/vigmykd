import pygame
from pygame import Surface

from context import GameContext
from controller.input_handler import InputHandler
from controller.input_model import PlayerInput
from event.manager import EventManager
from game.model import GameState
from network import GameServerClient
from network.udp.factory import Packets
from player import Player
from registry import registries
from view import Renderer, Renderable

from dataclasses import asdict
from uuid import UUID

from scene.manager import SceneManager


class Game:
    from view.system import ViewSystem

    # MVC
    controller: InputHandler
    model: GameState
    view: Renderer  # intermediate View part
    view_system: ViewSystem

    def __init__(
        self,
        ctx: GameContext,
        screen: Surface, 
        event_manager: EventManager,
        server_client: GameServerClient
    ):
        from scene.objects import limbo
        from view.system import ViewSystem

        from registry import registration_imports

        self.ctx = ctx
        self.screen = screen

        self.controller = InputHandler(self.ctx.assets_path)
        for mapping, action in ctx.cfg.keymap.items():
            self.controller.bind(mapping, action)

        self.server_client = server_client
        self.model = GameState(
            logger=ctx.logger,
            server_client=server_client
        )

        self.view = Renderer(self.screen, self.ctx.texture_manager, self.ctx)
        self.view_system = ViewSystem(self.ctx)

        player_adapter = registries.view_adapters[Player]
        if player_adapter is None:
            raise ValueError("No view adapter found for type Player")
        self.player_adapter = player_adapter

        self.renderables: dict[UUID, Renderable] = {}

        self.event_manager = event_manager

        self.scene_manager = SceneManager(
            initial=limbo.LimboScene(
                model=self.model,
                ctx=self.ctx,
            ),
            event_manager=event_manager,
            renderer=self.view
        )

        # self.model.start_match(self.ctx.auth.get_current_user(), uuid.uuid4())  # testing purpose

    def handle_input_prep(self, event: pygame.event.Event):
        if not self.scene_manager.handle_pygame_event(event):
            self.controller.handle_event(event)

    def tick(self):
        player_input = PlayerInput()
        mutations = self.controller.handle_input(self.ctx.logger)

        if mutations:
            for mutation in mutations:
                mutation(player_input)  # edits in-place

        self.event_manager.push()

        if self.model.client_player:
            self.model.buffer_input(self.model.client_player.player_id, player_input)
            current_tick = self.model.tick_idx
            input_payload = asdict(player_input)

            if self.model.is_in_match:
                self.ctx.logger.info(f"[CLIENT] SENDING UDP | Tick: {self.model.tick_idx} | Dir: {player_input.move_dir} | Positions: {self.model.client_player.position=!r}, {self.model.opponent_player.position=!r}")
                packet = Packets.player_move_state(input_payload, current_tick)
                msg_id = packet.msg_id
                self.model.server_client.enqueue(Packets.envelope(packet), msg_id)

        self.scene_manager.tick()

        self.model.advance()

    def render(self):
        self.view.drop_render_queue()

        self.scene_manager.render(self.view, self.view_system)

        self.view.draw_screen()
