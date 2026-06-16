import uuid

from enum import IntEnum

from geometry import BoundingBox2D
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_DUCK_HEIGHT

from generated.proto.v1 import packet_pb2 as packet_pb2


class Facing(IntEnum):
    NEG_X = 0
    POS_X = 1


class Player:
    player_id: uuid.UUID

    def __init__(
        self,
        player_id: uuid.UUID,
        name: str,
        is_client: bool,

        x: float = 0.0,
        y: float = 0.0,
        facing: Facing | None = None
    ):
        self.player_id = player_id
        self.name = name
        self.is_client = is_client

        self.x = x
        self.y = y

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.facing = facing

        self.is_on_ground = True
        self.is_ducking = False

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
    def get_bounding_box(self) -> BoundingBox2D:
        return BoundingBox2D(
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )

    def toggle_duck_height(self, duck: bool):
        self.is_ducking = duck
        self.height = PLAYER_DUCK_HEIGHT if duck else PLAYER_HEIGHT

    @property
    def can_jump(self) -> bool:
        return self.is_on_ground
