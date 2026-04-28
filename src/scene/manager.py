from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem


class SceneManager:
    current: Scene

    def __init__(self, initial: Scene):
        self.current = initial

    def switch(self, scene: Scene):
        if hasattr(self.current, "on_exit"):
            self.current.on_exit()

        self.current = scene

        if hasattr(self.current, "on_enter"):
            self.current.on_enter()

    def tick(self):
        self.current.tick()

    def render(self, view: Renderer, view_system: ViewSystem):
        self.current.render(view, view_system)
