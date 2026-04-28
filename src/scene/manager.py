from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem


class SceneManager:
    current: Scene

    def __init__(self, initial: Scene):
        self.current = initial

    def switch(self, scene: Scene):
        self.current = scene

    def tick(self):
        self.current.tick()

    def render(self, view: Renderer, view_system: ViewSystem):
        self.current.render(view, view_system)
