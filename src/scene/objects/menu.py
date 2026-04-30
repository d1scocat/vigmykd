from context import GameContext
from game.model import GameState
from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem

import pygame


class MenuScene(Scene):
    def __init__(self, model: GameState, ctx: GameContext):
        from registry import registries
        self.router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

    def tick(self):
        inputs = self.model.consume_inputs()
        self.router.simulate_route(inputs, self.model, self.ctx)

    def handle_pygame_event(self, event: pygame.event.Event):
        if event not in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
            pass

        mx, my = event.pos
        # iterate through buttons and interact

    def render(self, view: Renderer, view_system: ViewSystem):
        view_system.update(self.model)
        view_system.submit(view)

    def on_enter(self):
        pass

    def on_exit(self):
        pass
