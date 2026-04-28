from context import GameContext
from game.model import GameState
from scene.scene import Scene
from view import Renderer
from view.system import ViewSystem


class MenuScene(Scene):
    def __init__(self, model: GameState, ctx: GameContext):
        from registry import registries
        self.router = registries.consumers.router_by_tag("menu")

        self.model = model
        self.ctx = ctx

    def tick(self):
        inputs = self.model.consume_inputs()
        self.router.simulate_route(inputs, self.model, self.ctx)

    def render(self, view: Renderer, view_system: ViewSystem):
        view_system.update(self.model)
        view_system.submit(view)
