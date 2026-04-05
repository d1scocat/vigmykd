from game.model import GameState
from context import GameContext
from view import renderable_player  # dev test


def handle(dt: float, __: GameState, ctx: GameContext):
    speed = 100
    x, y = renderable_player.location
    renderable_player.location = (x + int(speed*dt), y)
