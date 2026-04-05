from context import GameContext
from pygame import Surface

from game import GameState, InputHandler
from game.controller.handlers.init_handlers import register_all
from game.view import Renderer


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

        self.view = Renderer(self.screen)

    def handle_input(self, dt: float):
        self.controller.handle_input(dt, self.model)

    def render(self):
        self.view.draw_screen()
