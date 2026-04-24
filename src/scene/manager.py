from game.game import Game
from scene.scene import Scene


class SceneManager:
    current: Scene

    def switch(self, scene: Scene):
        self.current = scene

    def tick(self):
        self.current.tick()

    def render(self, game: Game):
        self.current.render(game)
