from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

import json

import pygame

from context import GameContext
from game.model import GameState
from scene.router import SceneInputRouter
from ui.components.page import UIPage
from ui.components.textarea import UITextArea
from ui.deserializer import deserialize_into_ui
from ui.interaction import UIInteractionSystem
from view import Renderer
from view.system import ViewSystem
from world import World


class Scene(ABC):
    model: GameState
    ctx: GameContext
    input_router: SceneInputRouter
    action_mapping: dict[str, Callable[['Scene', GameState, GameContext], Any] | None]

    _loaded: bool = False  # problems may arise?

    def tick(self):
        self.model.server_client.pump()

        keys = pygame.key.get_pressed()
        if self.interaction.focused_component:
            component = self.interaction.focused_component
            if isinstance(component, UITextArea):
                component.update(keys)

        inputs = self.model.consume_inputs()
        self.input_router.simulate_route(inputs, self.model, self.ctx)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        perform = self.interaction.update(
            self.page.elements,
            mouse_pos,
            mouse_down
        )

        if perform is not None:
            action = self.find_action(perform)
            if action is not None:
                action(self, self.model, self.ctx)

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_exit(self):
        pass

    def load(self):
        if not self._loaded:
            self.on_load()
            self._loaded = True

    @abstractmethod
    def on_load(self):
        pass
    
    @abstractmethod
    def on_event(self, event: pygame.event.Event) -> bool:
        pass

    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        """
            Returns: True if the event is intercepted by the scene and should not
            be handled by the central input handler (e.g. textarea handling).
        """
        if self.interaction:
            self.interaction.handle_key(event, self.page.elements)

            focused = self.interaction.focused_component
            if focused and isinstance(focused, UITextArea):
                if focused.handle_event(event):
                    return True

        if hasattr(self, "on_event"):
            return self.on_event(event)
        return False

    def set_world(self, world: World | None):
        """Use only this function if you need to set the world of the current scene"""
        setattr(self, "__map", world)

    @property
    def world(self) -> World | None:
        if hasattr(self, "__map"):
            it = getattr(self, "__map")
            if isinstance(it, World):
                return it
        return None

    def render(
        self,
        view: Renderer,
        view_system: ViewSystem,
        render_alpha: float,
    ):
        view.drop_render_queue()

        self.page.process()
        self.page.resolve_layout(self.ctx.screen_size, self.ctx)
        self.page.submit_ui(view)

        view_system.update(self.model, render_alpha)
        view_system.submit(view)

        player = self.model.client_player
        offset = (0, 0)
        if player:
            own_world = self.world
            if own_world:
                own_world.prep_render(player.rect.to_pygame())
                offset = own_world.camera.offset if own_world else (0, 0)
                view.queue_static(own_world.render_surface, (0, 0))

        view.draw_screen(offset)

    def find_action(self, action_name: str) -> Callable[['Scene', GameState, GameContext], Any] | None:
        return self.action_mapping.get(action_name)

    @property
    @abstractmethod
    def page(self) -> UIPage:
        pass

    @property
    @abstractmethod
    def interaction(self) -> UIInteractionSystem:
        pass

    def get_ui(self, file_path: Path) -> UIPage:
        data = json.loads(file_path.read_text())
        return deserialize_into_ui(data)
