from registry import register_consumer

from controller.consumers import InputConsumer

from controller.input_model import PlayerInput
from context import GameContext
from game import GameState
from player import Player

@register_consumer
class MovementConsumer(InputConsumer):
    def consume(
        self,
        player: Player,
        state: GameState,
        ctx: GameContext,
        input: PlayerInput
    ):
        pass