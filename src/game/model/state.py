from logging import Logger
from uuid import UUID
from random import Random

from context import GameContext
from controller.input_model import PlayerInput
from network import GameServerClient
from player import Player, Position
from settings import MAX_REDUNDANCY_TICKS as REDUNDANCY, \
    SIMUL_DELAY_TICKS as DELAY

from generated.proto.v1 import packet_pb2 as packet_pb2


class GameState:
    _input_buffer: dict[int, dict[UUID | None, PlayerInput]]

    def __init__(self, logger: Logger, server_client: GameServerClient):
        self.server_client = server_client
        self.logger = logger

        self.tick_idx = 0
        self.network_offset = 0
        self.last_server_tick = 0

        self._input_buffer = {}
        self.rng = Random()
        self.is_in_match = False
        self.is_reconciling = False

        self.client_player: Player | None = None
        self.opponent_player: Player | None = None

    @property
    def players(self) -> dict[UUID, Player]:
        return {
            player.player_id: player
            for player in [self.client_player, self.opponent_player]
            if player
        }

    @property
    def estimated_server_tick(self):
        return self.tick_idx + self.network_offset

    def get_player(self, pid: UUID) -> Player | None:
        """
        Right now this simply does a dictionary lookup and this function
        exists for the purpose of future compatibility in case there will
        be a need for extra validity checks.
        """
        return self.players.get(pid)

    def set_client_player(self, player: Player):
        self.client_player = player

    def set_opponent_player(self, player: Player):
        self.opponent_player = player

    def prepare_match(
        self,
        rng_seed: int | float | str | bytes | bytearray | Random,
        initial_server_tick: int = 0
    ):
        if isinstance(rng_seed, Random):
            self.rng = rng_seed
        else:
            self.rng = Random(rng_seed)

        self.tick_idx = initial_server_tick
        self._input_buffer.clear()

    def start_match(self):
        if self.client_player is None or self.opponent_player is None:
            raise ValueError("Cannot start match if either of the players is None")

        self.is_in_match = True

    def _sync_offset(self, server_tick: int, last_client_tick: int):
        if server_tick <= self.last_server_tick:
            return

        self.network_offset = server_tick - last_client_tick
        self.last_server_tick = server_tick

    def reconcile(
        self,
        server_tick: int,
        last_client_tick: int,
        player_data: list[packet_pb2.PositionData],
        ctx: GameContext,
    ):
        self.logger.info(f"[NET] RECONCILE CALLED | Srv: {server_tick} | Players in packet: {len(player_data)}")

        if self.client_player is None or self.opponent_player is None:
            self.logger.warning("Cannot reconcile position if any player is None")
            return
        
        self._sync_offset(server_tick, last_client_tick)

        try:
            self.logger.info(f"[NET] Server sent UUIDs: {[data.uuid for data in player_data]}")
            self.logger.info(f"[NET] Local UUIDs: Client={self.client_player.player_id}, Opp={self.opponent_player.player_id}")
            player_pos = {
                UUID(data.uuid): Position.from_packet(data)
                for data in player_data
            }

            if len(player_pos) != 2:
                raise ValueError("Invalid player count")

            client_pos = player_pos.get(self.client_player.player_id)
            opponent_pos = player_pos.get(self.opponent_player.player_id)

            if not client_pos or not opponent_pos:
                raise ValueError("Could not map reconciliation UUIDs to active players")

            self.logger.info(f"[NET] Successfully parsed positions. Opponent new pos: {opponent_pos}")
        except Exception:
            self.logger.exception("Could not decode player position packets")
            return

        # opponent position is not being predicted
        self.opponent_player.apply_position(opponent_pos)
        self.logger.info(f"[NET] Applied opponent position. New Opponent Pos: {self.opponent_player.position}")

        if not self.client_player.matches_position(client_pos):
            self.logger.info(
                "Local player position diverged, reconcilling | Server: %r (current: %r)",
                client_pos, self.client_player.position
            )
            self.client_player.apply_position(client_pos)

            self.is_reconciling = True

            # resimulate for cleaner rendeing
            for tick_to_sim in range(last_client_tick + 1, self.tick_idx + 1):
                buffered = self._input_buffer.get(tick_to_sim, {})
                local_input = buffered.get(self.client_player.player_id)
                if local_input:
                    self.simulate_input(ctx, self.client_player, local_input)

            self.is_reconciling = False

        self.clear_redundant(last_client_tick)

    def simulate_input(self, ctx: GameContext, player: Player, player_input: PlayerInput):
        from registry import registries

        consumers = registries.consumers
        for consumer in consumers:
            consumer.consume(player, self, ctx, player_input)

    def buffer_input(self, player_id: UUID | None, player_input: PlayerInput):
        # network_offset is RTT, so one way latency is RTT / 2
        # +DELAY is leeway for network jitter

        # ...actually it might not be needed
        # delay = max(DELAY, (self.network_offset // 2) + DELAY)
        tick = self.tick_idx # + delay
        self.logger.info(f"[CLIENT] BUFFER | Tick: {tick} | Dir: {player_input.move_dir}")

        tick_buffer = self._input_buffer.setdefault(tick, {})
        tick_buffer[player_id] = player_input
        self._input_buffer[tick] = tick_buffer

    def consume_inputs(self) -> dict[UUID | None, PlayerInput]:
        return self._input_buffer.pop(self.tick_idx, {})

    def clear_redundant(self, last_client_tick: int | None = None):
        cutoff_tick = self.tick_idx - REDUNDANCY
        expired_time = [k for k in self._input_buffer if k <= cutoff_tick]
        for k in expired_time:
            del self._input_buffer[k]

        if last_client_tick is not None:
            expired_ack = [k for k in self._input_buffer if k <= last_client_tick]
            for k in expired_ack:
                del self._input_buffer[k]

    def advance(self):
        self.clear_redundant()
        self.tick_idx += 1
