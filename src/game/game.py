import pygame
from pygame import Surface

from context import GameContext
from controller.input_handler import InputHandler
from controller.input_model import PlayerInput
from event.manager import EventManager
from game.model import GameState
from player import Player
from registry import registries
from view import Renderer, Renderable
from view.adapter import ViewAdapter

from typing import Dict
from uuid import UUID

from scene.manager import SceneManager


class Game:
    from view.system import ViewSystem

    ctx: GameContext
    screen: Surface

    # MVC
    controller: InputHandler
    model: GameState
    view: Renderer  # intermediate View part
    view_system: ViewSystem

    player_adapter: ViewAdapter

    def __init__(self, ctx: GameContext, screen: Surface, event_manager: EventManager):
        from scene.objects import MenuScene
        from view.system import ViewSystem

        self.ctx = ctx
        self.screen = screen

        self.controller = InputHandler(self.ctx.assets_path)
        for mapping, action in ctx.cfg.keymap.items():
            self.controller.bind(mapping, action)

        self.model = GameState()

        self.view = Renderer(self.screen, self.ctx.texture_manager, self.ctx)
        self.view_system = ViewSystem(self.ctx)

        player_adapter = registries.view_adapters[Player]
        if player_adapter is None:
            raise ValueError("No view adapter found for type Player")
        self.player_adapter = player_adapter

        self.renderables: Dict[UUID, Renderable] = {}
        
        self.event_manager = self.event_manager

        self.scene_manager = SceneManager(
            initial=MenuScene(
                model=self.model,
                ctx=self.ctx,
            ),
            event_manager=event_manager
        )

        # self.model.start_match(self.ctx.auth.get_current_user(), uuid.uuid4())  # testing purpose

    def handle_input_prep(self, event: pygame.event.Event):
        self.controller.handle_event(event)
        self.scene_manager.handle_pygame_event(event)

    def simulate(self, inputs: Dict[UUID | None, PlayerInput]):
        consumers = registries.consumers

        for player_id, input in inputs.items():
            player: Player | None = None

            if player_id:
                player = self.model.get_player(player_id)

            for consumer in consumers:
                consumer.consume(player, self.model, self.ctx, input)

    def tick(self):
        input = PlayerInput()
        mutations = self.controller.handle_input(self.ctx.logger)

        if mutations:
            for mutation in mutations:
                mutation(input)  # edits in-place

        self.model.buffer_input(self.ctx.local_player_id, input)

        self.scene_manager.tick()

        self.model.advance()

    def render(self):
        self.view.drop_queue()

        self.scene_manager.render(self.view, self.view_system)

        self.view.draw_screen()
