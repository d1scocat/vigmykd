from dataclasses import dataclass, field
from enum import IntEnum

from settings import *

from generated.proto.v1 import packet_pb2 as packet_pb2


class Facing(IntEnum):
    NEG_X = 0
    POS_X = 1


@dataclass
class PlayerPhysics:
    dash_timer: int = 0
    coyote_timer: int = 0
    jump_buffer_timer: int = 0
    last_jump_pressed: bool = False
    last_dash_pressed: bool = False
    hang_timer: int = 0
    invulnerable_timer: int = 0
    heavy_gravity_timer: int = 0
    light_gravity_timer: int = 0
    stun_timer: int = 0


@dataclass
class PlayerCooldowns:
    brake_dash: int = 0
    reverse_dash: int = 0
    hang: int = 0
    parry: int = 0

    heavy: int = 0
    light: int = 0
    normal: int = 0

    push: int = 0
    stomp: int = 0
    punch: int = 0

    def reduce(self):
        self.brake_dash = max(0, self.brake_dash - 1)
        self.reverse_dash = max(0, self.reverse_dash - 1)
        self.hang = max(0, self.hang - 1)
        self.parry = max(0, self.parry - 1)
        self.heavy = max(0, self.heavy - 1)
        self.light = max(0, self.light - 1)
        self.normal = max(0, self.normal - 1)

        self.push = max(0, self.push - 1)
        self.stomp = max(0, self.stomp - 1)
        self.punch = max(0, self.punch - 1)

    @property
    def can_brake_dash(self):
        return self.brake_dash == 0

    def cooldown_brake_dash(self):
        self.brake_dash = BRAKE_DASH_COOLDOWN_TICKS

    @property
    def can_reverse_dash(self):
        return self.reverse_dash == 0

    def cooldown_reverse_dash(self):
        self.reverse_dash = REVERSE_DASH_COOLDOWN_TICKS

    @property
    def can_hang(self):
        return self.hang == 0

    def cooldown_hang(self):
        self.hang = HANG_COOLDOWN_TICKS

    @property
    def can_parry(self):
        return self.parry == 0

    def cooldown_parry(self):
        self.parry = PARRY_COOLDOWN_TICKS

    @property
    def can_heavy(self):
        return self.heavy == 0

    def cooldown_heavy(self):
        self.heavy = HEAVY_COOLDOWN_TICKS

    @property
    def can_light(self):
        return self.light == 0

    def cooldown_light(self):
        self.light = LIGHT_COOLDOWN_TICKS

    @property
    def can_normal(self):
        return self.normal == 0

    def cooldown_normal(self):
        self.normal = NORMAL_COOLDOWN_TICKS

    @property
    def can_push(self):
        return self.push == 0

    def cooldown_push(self):
        self.push = PUSH_COOLDOWN_TICKS

    @property
    def can_stomp(self):
        return self.stomp == 0

    def cooldown_stomp(self):
        self.stomp = STOMP_COOLDOWN_TICKS

    @property
    def can_punch(self):
        return self.punch == 0

    def cooldown_punch(self):
        self.punch = PUNCH_COOLDOWN_TICKS


@dataclass
class Combo:
    hits: int = 0
    timer: int = 0
    broken: bool = True


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
    cooldowns: PlayerCooldowns = field(default_factory=PlayerCooldowns)
    combo: Combo = field(default_factory=Combo)

    @classmethod
    def from_packet(cls, packet: packet_pb2.ReconcileData):
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
            ),

            physics=PlayerPhysics(
                dash_timer=packet.dash_timer,
                coyote_timer=packet.coyote_timer,
                jump_buffer_timer=packet.jump_buffer_timer,
                last_dash_pressed=packet.last_dash_pressed,
                last_jump_pressed=packet.last_jump_pressed,
                hang_timer=packet.hang_timer,
                invulnerable_timer=packet.invulnerable_timer,
                heavy_gravity_timer=packet.heavy_gravity_timer,
                light_gravity_timer=packet.light_gravity_timer,
                stun_timer=packet.stun_timer,
            ),

            cooldowns=PlayerCooldowns(
                brake_dash=packet.brake_dash,
                reverse_dash=packet.reverse_dash,
                hang=packet.hang,
                parry=packet.parry,

                heavy=packet.heavy,
                light=packet.light,
                normal=packet.normal,

                push=packet.push,
                stomp=packet.stomp,
                punch=packet.punch,
            ),

            combo=Combo(
                hits=packet.combo_hits,
                timer=packet.combo_timer,
                broken=packet.combo_broken,
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


@dataclass
class Snapshot:
    position: Position
    mana: int
    health: float
