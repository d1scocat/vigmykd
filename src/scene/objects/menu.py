from context import GameContext
from game.model import GameState
from scene.scene import Scene
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

import pygame


class MenuScene(Scene):
    def __init__(self, model: GameState, ctx: GameContext):
        from registry import registries
        self.router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

        self.ui_interaction = UIInteractionSystem()
        self.ui_page = ... # will fill in later

    def tick(self):
        inputs = self.model.consume_inputs()
        self.router.simulate_route(inputs, self.model, self.ctx)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        self.ui_interaction.update(
            self.ui_page.elements,
            mouse_pos,
            mouse_down
        )

    def handle_pygame_event(self, event: pygame.event.Event):
        if event not in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
            pass

        mx, my = event.pos

    def render(self, view: Renderer, view_system: ViewSystem):
        view.drop_queue()

        self.ui_page.resolve_layout(self.ctx.screen_size)
        self.ui_page.submit_ui(view)

        view_system.update(self.model)
        view_system.submit(view)

    def on_enter(self):
        pass

    def on_exit(self):
        pass
