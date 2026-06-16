from registry import register_consumer

from controller.consumers.input_consumer import InputConsumer

from controller.input_model import PlayerInput
from context import GameContext
from game.model import GameState
from player import Player


@register_consumer(tags=[""])
class MovementConsumer(InputConsumer):
    def consume(
        self,
        player: Player | None,
        state: GameState,
        ctx: GameContext,
        input: PlayerInput
    ):
        ctx.logger.info("Received input %s for player %s", input, player.id if player else None)
        if not player:
            return  # Not the appropriate system for movement handling

        # Implement physics later!
