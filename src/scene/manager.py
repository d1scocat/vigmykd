from event import EventManager
from event.events import ScenePreExitEvent, \
    ScenePostEnterEvent, \
    ScenePostExitEvent, \
    ScenePreEnterEvent, \
    ScenePreLoadEvent, \
    ScenePostLoadEvent, \
    SceneSwitchRequestEvent, \
    PrepareSceneRequestEvent
from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem

import pygame


class SceneManager:
    current: Scene
    event_manager: EventManager

    def __init__(self, initial: Scene, event_manager: EventManager, renderer: Renderer):
        self.event_manager = event_manager
        self.renderer = renderer

        self._enter_scene(initial)

        self.event_manager.register_listener(SceneSwitchRequestEvent, self.switch_req_handler)
        self.event_manager.register_listener(PrepareSceneRequestEvent, self.prep_scene_handler)

    def switch(self, scene: Scene):
        self._exit_scene(self.renderer)
        self._enter_scene(scene)

    def switch_req_handler(self, event: SceneSwitchRequestEvent):
        self.switch(event.target)

    def prep_scene_handler(self, event: PrepareSceneRequestEvent):
        event.scene.load()

    def tick(self):
        self.current.tick()

    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        if hasattr(self.current, "handle_pygame_event"):
            return self.current.handle_pygame_event(event)
        return False

    def render(self, view: Renderer, view_system: ViewSystem, render_alpha: float):
        self.current.render(view, view_system, render_alpha, self.current.ctx)

    def _enter_scene(self, scene: Scene):
        self.event_manager.invoke_event(ScenePreLoadEvent(scene))

        scene.load()

        self.event_manager.invoke_event(ScenePostLoadEvent(scene))

        self.event_manager.invoke_event(ScenePreEnterEvent(scene))

        self.current = scene
        self.current.on_enter()

        self.event_manager.invoke_event(ScenePostEnterEvent(scene))

    def _exit_scene(self, renderer: Renderer):
        self.event_manager.invoke_event(ScenePreExitEvent(self.current))

        renderer.clear_texture_scale_cache()
        self.current.on_exit()

        self.event_manager.invoke_event(ScenePostExitEvent(self.current))
