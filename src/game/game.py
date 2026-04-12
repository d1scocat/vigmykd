from context import GameContext

import pygame
from pygame import Surface

from game import GameState
from controller import InputHandler, PlayerInput
from controller.handlers.init_handlers import register_all
from view import Renderer


class Game:
    ctx: GameContext
    screen: Surface

    # MVC
    controller: InputHandler
    model: GameState
    view: Renderer

    def __init__(self, ctx: GameContext, screen: Surface):
        self.ctx = ctx
        self.screen = screen

        self.controller = InputHandler()
        register_all(self.controller)

        for mapping, action in ctx.cfg.keymap.items():
            self.controller.bind(mapping, action)

        self.model = GameState()

        self.view = Renderer(self.screen, self.ctx.texture_manager, self.ctx)

    def handle_input_prep(self, event: pygame.event.Event):
        self.controller.handle_event(event)

    def tick(self):
        local_player_id = ...  # don't mind

        input = PlayerInput()
        mutations = self.controller.handle_input(self.ctx)
        if mutations:
            for mutation in mutations:
                input = mutation(input)
        self.model.buffer_input(local_player_id, input)

        inputs = self.model.consume_inputs()
        # what now?

        self.model.advance()

    def render(self):
        self.screen.fill((0,0,0))

        from view import renderable_player
        self.view.draw_renderable(renderable_player)
