from controller.input_model import PlayerInput
from context import GameContext
from game.model import GameState
from player import Player

from abc import ABC, abstractmethod


class InputConsumer(ABC):
    """
    An abstract class representing an arbitrary input consumer (input system).
    A consumer handles a specific part of a PlayerInput object and modifies
    relevant game data. An example of an InputConsumer can be a movement input
    consumer, which cares about movement-related changes invoked by the
    PlayerInput object and changes position/velocity-related information about
    the players.
    """
    @abstractmethod
    def consume(
        self,
        player: Player | None,
        state: GameState,
        ctx: GameContext,
        player_input: PlayerInput
    ):
        """
        Consumes the provided player input and executes specific actions
        or/and modifications on the current game state.
        Arguments "state" and "ctx" are provided for the consumer to be
        able to interact with the game.
        """
        pass
