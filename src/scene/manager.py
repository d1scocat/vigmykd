from event import EventManager
from event.events import scene_enter, scene_exit
from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem

import pygame


class SceneManager:
    current: Scene
    event_manager: EventManager

    def __init__(self, initial: Scene, event_manager: EventManager):
        self.current = initial
        self.event_manager = event_manager

    def switch(self, scene: Scene):
        self.event_manager.invoke_event(scene_exit.ScenePreExitEvent(self.current))

        if hasattr(self.current, "on_exit"):
            self.current.on_exit()
        self.event_manager.invoke_event(scene_exit.ScenePostExitEvent(self.current))

        self.event_manager.invoke_event(scene_enter.ScenePreEnterEvent(scene))
        self.current = scene

        if hasattr(self.current, "on_enter"):
            self.current.on_enter()
        self.event_manager.invoke_event(scene_enter.ScenePostEnterEvent(scene))

    def tick(self):
        self.current.tick()
    
    def handle_pygame_event(self, event: pygame.event.Event):
        if hasattr(self.current, "handle_pygame_event"):
            self.current.handle_pygame_event(event)

    def render(self, view: Renderer, view_system: ViewSystem):
        self.current.render(view, view_system)
