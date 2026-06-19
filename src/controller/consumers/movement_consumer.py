from registry import register_consumer

from controller.consumers.input_consumer import InputConsumer

from controller.input_model import PlayerInput
from context import GameContext
from game.model import GameState
from player import Facing, Player

from settings import MOVE_SPEED, \
    GRAVITY_RISE, \
    GRAVITY_FALL, \
    TERMINAL_VELOCITY, \
    JUMP_FORCE, \
    DASH_SPEED, \
    DASH_DURATION_TICKS, \
    ACCEL_X, \
    DECEL_X, \
    DASH_PLUNGE_SPEED, \
    MAX_JUMP_FORCE, \
    AIR_MOVE_SPEED, \
    AIR_ACCEL_X, \
    AIR_DECEL_X, \
    FAST_FALL_MULTIPLIER, \
    AIR_DRAG, \
    PLAYER_HEIGHT, \
    PLAYER_WIDTH


@register_consumer(tags=["match"])
class MovementConsumer(InputConsumer):
    def consume(
        self,
        player: Player | None,
        state: GameState,
        ctx: GameContext,
        player_input: PlayerInput
    ):
        if not player:
            return

        world = state.world
        if not world:
            return

        # === === === dashing === === === #
        if player_input.dash and not player.position.is_dashing:
            player.position.is_dashing = True
            player.position.physics.dash_timer = DASH_DURATION_TICKS

            # plunge down
            if not player.position.is_grounded and player_input.duck:
                player.position.vel_x = 0.0
                player.position.vel_y = min(DASH_PLUNGE_SPEED, TERMINAL_VELOCITY)

            # dashing in place (jumping up high)
            elif player.position.is_grounded and player_input.move_dir == 0 and not player_input.duck:
                player.position.vel_y = MAX_JUMP_FORCE
                player.position.is_grounded = False

            # just dashing
            else:
                dash_dir = player_input.move_dir if player_input.move_dir != 0 else 1
                player.position.vel_x = dash_dir * DASH_SPEED

        if player.position.is_dashing:
            player.position.physics.dash_timer -= 1
            if player.position.physics.dash_timer <= 0:
                player.position.is_dashing = False

        # === === === x movement === === ===
        if player.position.is_dashing:
            if not player.position.is_grounded and player_input.duck:
                player.position.vel_x = 0.0  # no x-axis movement during plunge
            else:
                pass  # ignore normal movement and maintain momentum

        else:
            is_airborne = not player.position.is_grounded

            current_move_speed = AIR_MOVE_SPEED if is_airborne else MOVE_SPEED
            current_accel_x = AIR_ACCEL_X if is_airborne else ACCEL_X
            current_decel_x = AIR_DECEL_X if is_airborne else DECEL_X

            if player_input.move_dir != 0:
                target_vel = player_input.move_dir * current_move_speed

                #if (player_input.move_dir > 0 and player.position.vel_x < 0) or \
                #    (player_input.move_dir < 0 and player.position.vel_x > 0):
                # decelerating?
                if (player_input.move_dir * player.position.vel_x) < 0:
                    self._decelerate(player, current_decel_x)

                # accelerating then
                else:
                    player.position.vel_x += player_input.move_dir * current_accel_x

                # clamp
                if (player_input.move_dir > 0 and player.position.vel_x > target_vel) or \
                    (player_input.move_dir < 0 and player.position.vel_x < target_vel):
                    player.position.vel_x = target_vel

            # slowing down due to no input
            else:
                self._decelerate(player, current_decel_x)

        if not player.position.is_grounded and not player.position.is_dashing:
            player.position.vel_x *= AIR_DRAG

        # update facing
        if player.position.vel_x > 0:
            player.position.facing = Facing.POS_X
        elif player.position.vel_x < 0:
            player.position.facing = Facing.NEG_X

        # === === === y movement: jump === === ===
        if player_input.jump and player.position.is_grounded and not player_input.duck:
            player.position.vel_y = JUMP_FORCE
            player.position.is_grounded = False

        # === === === y movement: gravity === === ===
        if not player.position.is_grounded:
            if player.position.vel_y < 0:
                if not player_input.jump:
                    player.position.vel_y += GRAVITY_RISE * FAST_FALL_MULTIPLIER
                else:
                    player.position.vel_y += GRAVITY_RISE
            else:
                player.position.vel_y += GRAVITY_FALL

            if player.position.vel_y > TERMINAL_VELOCITY:
                player.position.vel_y = TERMINAL_VELOCITY

        # === === === pos update === === ===
        player.position.x += player.position.vel_x
        player.position.y += player.position.vel_y

        rect = player.rect

        # === === === x axis === === ==
        coll_rect = world.headless.get_collision(rect)

        if coll_rect:
            if player.position.vel_x > 0:
                player.position.x = coll_rect.left - PLAYER_WIDTH
            elif player.position.vel_x < 0:
                player.position.x = coll_rect.right

            player.position.vel_x = 0

        # === === === y axis === === ==
        if coll_rect:
            if player.position.vel_y > 0:
                player.position.y = coll_rect.top - PLAYER_HEIGHT
                player.position.is_grounded = True
            elif player.position.vel_y < 0:
                player.position.y = coll_rect.bottom

            player.position.vel_y = 0

    def _decelerate(self, player: Player, current_decel_x: float):
        if player.position.vel_x > 0:
            player.position.vel_x -= current_decel_x
            if player.position.vel_x < 0:
                player.position.vel_x = 0.0

        else:
            player.position.vel_x += current_decel_x
            if player.position.vel_x > 0:
                player.position.vel_x = 0.0
