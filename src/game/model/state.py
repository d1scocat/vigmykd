from typing import Dict
from uuid import UUID
from random import Random
from settings import MAX_REDUNDANCY_TICKS as REDUNDANCY, \
    SIMUL_DELAY_TICKS as DELAY

from controller import PlayerInput
from player import Player


class GameState:
    _tick: int
    _input_buffer: Dict[int, Dict[UUID, PlayerInput]]
    rng: Random  # later will request per-game fetching from server

    def __init__(self):
        self._tick = 0
        self._input_buffer = {}
        self.rng = Random("this will not be static later")

        self.players: Dict[UUID, Player] = {}
    
    def get_player(self, id: UUID) -> Player | None:
        """
        Right now this simply does a dictionary lookup and this function
        exists for the purpose of future compatibility in case there will
        be a need for extra validity checks.
        """
        return self.players.get(id)

    def sync_rng(self, seed: int | float | str | bytes | bytearray | Random):
        """
        This should be used if at any point the client needs to sync their
        RNG instance with the server (e.g. the beginning of a game match).

        Arguments:
            seed: the seed to use for the new RNG instance, or the new instance
        """
        if isinstance(seed, Random):
            self.rng = seed
        else:
            self.rng = Random(seed)

    def buffer_input(self, player_id: UUID, input: PlayerInput):
        tick = self._tick + DELAY

        tick_buffer = self._input_buffer.setdefault(tick, {})
        tick_buffer[player_id] = input
        self._input_buffer[tick] = tick_buffer

    def consume_inputs(self):
        return self._input_buffer.pop(self._tick, {})

    def clear_redundant(self):
        if self._tick - REDUNDANCY in self._input_buffer:
            self._input_buffer.pop(self._tick - REDUNDANCY)

    def advance(self):
        self.clear_redundant()
        self._tick += 1
