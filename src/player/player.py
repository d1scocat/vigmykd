import uuid

from anim import AnimationData
from geometry import Rect
from player import Facing, Position, Snapshot
from settings import *


class Player:
    player_id: uuid.UUID
    anim: AnimationData

    def __init__(
        self,
        player_id: uuid.UUID,
        name: str,
        is_client: bool,

        x: float,
        y: float,
        facing: Facing,
    ):
        self.player_id = player_id
        self.name = name
        self.is_client = is_client

        self.position = Position(x, y, facing)

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.is_on_ground = True
        self.is_ducking = False

        self.mana = MAX_MANA
        self.health = MAX_HEALTH

    def snap(self) -> Snapshot:
        return Snapshot(self.position, self.mana)

    def apply_snapshot(self, snapshot: Snapshot):
        self.position = snapshot.position
        self.mana = snapshot.mana

    def matches_position(self, position: Position, epsilon: float = 0.01):
        return self.position.matches_position(position, epsilon)

    @property
    def rect(self) -> Rect:
        height = PLAYER_DUCK_HEIGHT if self.position.is_ducking else PLAYER_HEIGHT

        return Rect(
            self.position.x,
            self.position.y,
            PLAYER_WIDTH,
            height
        )

    @classmethod
    def from_packet(cls, player_data: packet_pb2.PlayerData, is_client: bool):
        """Can raise!"""
        player_id = uuid.UUID(player_data.uuid)
        name = player_data.name
        position = player_data.position

        x, y = position.x, position.y
        match position.facing:
            case packet_pb2.Facing.FACING_NEG_X:
                facing = Facing.NEG_X
            case packet_pb2.Facing.FACING_POS_X:
                facing = Facing.POS_X
            case _:
                raise ValueError(
                    f"Facing of packet is not FACING_NEG_X or FACING_POS_X ({position.facing})"
                )

        return cls(player_id, name, is_client, x, y, facing)

    @property
    def can_jump(self) -> bool:
        return self.is_on_ground
