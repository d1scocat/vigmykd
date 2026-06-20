import pygame
import uuid

from dataclasses import dataclass, field
from enum import IntEnum

from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_DUCK_HEIGHT

from generated.proto.v1 import packet_pb2 as packet_pb2


class Facing(IntEnum):
    NEG_X = 0
    POS_X = 1


@dataclass
class PlayerPhysics:
    dash_timer: int = 0
    coyote_timer: int = 0
    jump_buffer_timer: int = 0


@dataclass
class Position:
    x: float
    y: float
    facing: Facing
    vel_x: float = 0
    vel_y: float = 0
    is_ducking: bool = False
    is_dashing: bool = False
    is_grounded: bool = False
    physics: PlayerPhysics = field(default_factory=PlayerPhysics)

    @classmethod
    def from_packet(cls, packet: packet_pb2.PositionData):
        return cls(
            x=packet.x,
            y=packet.y,
            vel_x=packet.vel_x,
            vel_y=packet.vel_y,
            is_ducking=packet.is_ducking,
            is_dashing=packet.is_dashing,
            is_grounded=packet.is_grounded,

            facing=(
                Facing.NEG_X
                if packet.facing == packet_pb2.Facing.FACING_NEG_X
                else Facing.POS_X
            )
        )

    def matches_position(self, other: 'Position', epsilon: float = 0.01):
        return self.facing == other.facing and \
            abs(self.x - other.x) <= epsilon and \
            abs(self.y - other.y) <= epsilon and \
            abs(self.vel_x - other.vel_x) <= epsilon and \
            abs(self.vel_y - other.vel_y) <= epsilon and \
            self.is_ducking == other.is_ducking and \
            self.is_dashing == other.is_dashing and \
            self.is_grounded == other.is_grounded


class Player:
    player_id: uuid.UUID

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

    def apply_position(self, position: Position):
        self.position = position

    def matches_position(self, position: Position, epsilon: float = 0.01):
        return self.position.matches_position(position, epsilon)

    @property
    def rect(self) -> pygame.Rect:
        height = PLAYER_DUCK_HEIGHT if self.position.is_ducking else PLAYER_HEIGHT

        return pygame.Rect(
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
