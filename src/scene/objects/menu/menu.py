from context import GameContext
from game.model import GameState
from scene.objects.menu import actions
from scene.scene import Scene
from ui.components.page import UIPage
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem

import pygame
import uuid

from typing import Any, Callable


class MenuScene(Scene):
    def __init__(self, model: GameState, ctx: GameContext):
        from registry import registries
        self.router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

        self.ui_interaction = UIInteractionSystem()

        local = ctx.local_player_id or uuid.uuid4()
        authenticated = model.get_player(local) is not None

        self._ui_page = self.get_ui(
            ctx.ui_path / f"main-menu-{'' if authenticated else 'un'}authenticated.json"
        )

        self.action_mapping = {
            "show_login_overlay": actions.show_login_overlay,
            "open_settings": ...,
            "exit": ...
        }
    
    @property
    def page(self) -> UIPage:
        return self._ui_page

    def tick(self):
        inputs = self.model.consume_inputs()
        self.router.simulate_route(inputs, self.model, self.ctx)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        perform = self.ui_interaction.update(
            self.page.elements,
            mouse_pos,
            mouse_down
        )

        if perform is not None:
            action = self.find_action(perform)
            if action is not None:
                action(self, self.ctx)

    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        if event not in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
            pass
        pass

    def render(self, view: Renderer, view_system: ViewSystem):
        view.drop_render_queue()

        self.page.process()
        self.page.resolve_layout(self.ctx.screen_size, self.ctx)
        self.page.submit_ui(view)

        view_system.update(self.model)
        view_system.submit(view)

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def find_action(self, action_name: str) -> Callable[[Scene, GameContext], Any] | None:
        return self.action_mapping.get(action_name)
