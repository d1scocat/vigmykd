import pygame
from pygame import Surface

from context import GameContext
from controller import InputHandler, PlayerInput
from game import GameState
from player import Player
from view import Renderer, Renderable
from view.adapter.player import PlayerAdapter

from typing import Dict
from uuid import UUID


class Game:
    ctx: GameContext
    screen: Surface

    # MVC
    controller: InputHandler
    model: GameState
    view: Renderer

    player_adapter: PlayerAdapter

    def __init__(self, ctx: GameContext, screen: Surface):
        self.ctx = ctx
        self.screen = screen

        self.controller = InputHandler()
        # register_all(self.controller) replace later with mutators

        for mapping, action in ctx.cfg.keymap.items():
            self.controller.bind(mapping, action)

        self.model = GameState()

        self.view = Renderer(self.screen, self.ctx.texture_manager, self.ctx)

        self.player_adapter = self.ctx.registries.view_adapters[Player]

        self.renderables: Dict[UUID, Renderable] = {}

    def handle_input_prep(self, event: pygame.event.Event):
        self.controller.handle_event(event)
    
    def simulate(self, inputs: Dict[UUID, PlayerInput]):
        consumers = self.ctx.registries.consumers
        
        for player_id, input in inputs.items():
            player = self.model.get_player(player_id)

            if not player:
                continue

            for consumer in consumers:
                consumer.consume(player, self.model, self.ctx, input)

    def tick(self):
        local_player_id = self.ctx.auth.get_current_user()
        if local_player_id is not None:
            input = PlayerInput()
            mutations = self.controller.handle_input(self.ctx)
            if mutations:
                for mutation in mutations:
                    mutation(input)  # edits in-place
            self.model.buffer_input(local_player_id, input)

            inputs = self.model.consume_inputs()
            self.simulate(inputs)

        self.model.advance()

    def render(self):
        self.view.drop_queue()

        for player in self.model.players.values():
            if player.id not in self.renderables:
                self.renderables[player.id] = self.player_adapter.create(player)

            renderable = self.renderables[player.id]
            self.player_adapter.update(player, renderable)
            
            self.view.queue_renderable(renderable)
        
        self.view.draw_screen()
