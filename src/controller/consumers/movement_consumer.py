from registry import register_consumer

from controller.consumers.input_consumer import InputConsumer

from controller.input_model import PlayerInput
from context import GameContext
from game.model import GameState
from player import Player

from settings import MOVE_SPEED, \
    GRAVITY_RISE, \
    GRAVITY_FALL, \
    JUMP_CUT_SCALAR, \
    TERMINAL_VELOCITY, \
    JUMP_FORCE, \
    DASH_SPEED, \
    DASH_DURATION_TICKS, \
    ACCEL_X, \
    DECEL_X


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
            return  # Not the appropriate system for movement handling

        # === === === dashing === === === #
        if player_input.dash and not player.position.is_dashing:
            player.position.is_dashing = True
            player.position.physics.dash_timer = DASH_DURATION_TICKS

            dash_dir = player_input.move_dir if player_input.move_dir != 0 else 1
            player.position.vel_x = dash_dir * DASH_SPEED

        if player.position.is_dashing:
            player.position.physics.dash_timer -= 1
            if player.position.physics.dash_timer <= 0:
                player.position.is_dashing = False

        # === === === x movement === === ===
        if player.position.is_dashing:
            pass  # ignore normal movement and maintain momentum

        elif player_input.move_dir != 0:
            target_vel = player_input.move_dir * MOVE_SPEED
            if (player_input.move_dir > 0 and player.position.vel_x < 0) or \
               (player_input.move_dir < 0 and player.position.vel_x > 0):

                if player.position.vel_x > 0:
                    player.position.vel_x -= DECEL_X
                    if player.position.vel_x < 0: player.position.vel_x = 0.0
                else:
                    player.position.vel_x += ACCEL_X
                    if player.position.vel_x > 0: player.position.vel_x = 0.0
            else:
                player.position.vel_x += player_input.move_dir * ACCEL_X

            # clamp
            if player_input.move_dir > 0 and player.position.vel_x > target_vel:
                player.position.vel_x = target_vel
            elif player_input.move_dir < 0 and player.position.vel_x < target_vel:
                player.position.vel_x = target_vel

        else:
            if player.position.vel_x > 0:
                player.position.vel_x -= DECEL_X
                if player.position.vel_x < 0:
                    player.position.vel_x = 0.0
            elif player.position.vel_x < 0:
                player.position.vel_x += DECEL_X
                if player.position.vel_x > 0:
                    player.position.vel_x = 0.0

        # === === === y movement: jump === === ===
        if player_input.jump and player.position.is_grounded and not player_input.duck:
            player.position.vel_y = JUMP_FORCE
            player.position.is_grounded = False
            player.position.physics.has_cut_jump = False
            
            #if not state.is_reconciling:
            #    ctx.audio.play('jump_sound')
            #    ctx.particles.spawn('jump_dust', player.position.x, player.position.y)

        # === === === y movement: gravity === === ===
        if not player.position.is_grounded:
            if not player_input.jump and \
                player.position.vel_y < 0 and \
                    not player.position.physics.has_cut_jump:
                player.position.vel_y *= JUMP_CUT_SCALAR
                player.position.physics.has_cut_jump = True

            if player.position.vel_y < 0:
                player.position.vel_y += GRAVITY_RISE
            else:
                player.position.vel_y += GRAVITY_FALL

            if player.position.vel_y > TERMINAL_VELOCITY:
                player.position.vel_y = TERMINAL_VELOCITY

        # === === === pos update === === ===
        player.position.x += player.position.vel_x
        player.position.y += player.position.vel_y

        # === === === collision, ground === === ===
        floor_y = 400.0  # (stub!)
        if player.position.y >= floor_y:
            player.position.y = floor_y
            player.position.vel_y = 0.0
            player.position.is_grounded = True
