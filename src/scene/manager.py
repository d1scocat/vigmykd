from event import EventManager
from event.events import ScenePreExitEvent, \
    ScenePostEnterEvent, \
    ScenePostExitEvent, \
    ScenePreEnterEvent
from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem

import pygame


class SceneManager:
    current: Scene
    event_manager: EventManager

    def __init__(self, initial: Scene, event_manager: EventManager):
        self.event_manager = event_manager

        self._enter_scene(initial)

    def switch(self, scene: Scene, renderer: Renderer):
        self._exit_scene(renderer)
        self._enter_scene(scene)

    def tick(self):
        self.current.do_tick()

    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        if hasattr(self.current, "handle_pygame_event"):
            return self.current.handle_pygame_event(event)
        return False

    def render(self, view: Renderer, view_system: ViewSystem):
        self.current.render(view, view_system)

    def _enter_scene(self, scene: Scene):
        self.event_manager.invoke_event(ScenePreEnterEvent(scene))
        self.current = scene

        if hasattr(self.current, "on_enter"):
            self.current.on_enter()
        self.event_manager.invoke_event(ScenePostEnterEvent(scene))

    def _exit_scene(self, renderer: Renderer):
        self.event_manager.invoke_event(ScenePreExitEvent(self.current))

        renderer.clear_texture_scale_cache()

        if hasattr(self.current, "on_exit"):
            self.current.on_exit()
        self.event_manager.invoke_event(ScenePostExitEvent(self.current))
