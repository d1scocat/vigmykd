from context import GameContext
from controller.consumers.input_consumer import InputConsumer
from controller.input_model import PlayerInput
from game.model import GameState
from player import Player

from typing import Dict, List, Optional
from uuid import UUID


class SceneInputRouter:
    def __init__(self, consumers: List[InputConsumer]):
        self.consumers = consumers

    def simulate_route(
        self,
        inputs: Dict[Optional[UUID], PlayerInput],
        model: GameState,
        ctx: GameContext
    ):
        for pid, input in inputs.items():
            player: Optional[Player] = None
            if pid:
                player = model.get_player(pid)

            for consumer in self.consumers:
                consumer.consume(player=player, state=model, ctx=ctx, input=input)
