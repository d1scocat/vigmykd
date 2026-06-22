from registry import register_consumer

from controller.consumers.input_consumer import InputConsumer

from controller.input_model import PlayerInput
from context import GameContext
from game.model import GameState
from geometry import Rect
from player import Facing, Player
from world import World

from settings import *


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

        player.position.cooldowns.reduce()

        self._handle_dash(player, player_input)
        self._handle_x_axis(player, player_input)
        self._handle_coyote(player)
        self._handle_jump(player, player_input)
        self._handle_hanging(player, player_input)
        self._handle_gravity(player, player_input)
        self._handle_x_collision(player, world)
        self._handle_y_collision(player, world)

        self._prepare_attacking(player, player_input)

        other_player = state.opponent_player
        if other_player is not None:
            self._handle_push(player, player_input, [other_player])
            self._handle_stomp(player, player_input, [other_player])
            self._handle_punch(player, player_input, [other_player])

    def _handle_dash(self, player: Player, player_input: PlayerInput):
        dash_just_pressed = player_input.dash and not player.position.physics.last_dash_pressed
        can_dash = player.mana >= DASH_MANA_COST

        if dash_just_pressed and not player.position.is_dashing and can_dash:
            player.position.is_dashing = True
            player.position.physics.dash_timer = DASH_DURATION_TICKS + 1
            player.position.physics.coyote_timer = 0
            player.mana -= DASH_MANA_COST

            # plunge down
            if not player.position.is_grounded and player_input.duck:
                player.position.vel_x = 0.0
                player.position.vel_y = min(DASH_PLUNGE_SPEED, TERMINAL_VELOCITY)

            # dashing in place (jumping up high)
            elif player.position.is_grounded and player_input.move_dir == 0 and not player_input.duck:
                player.position.vel_x = 0.0
                player.position.vel_y = MAX_JUMP_FORCE
                player.position.is_grounded = False

            # just dashing
            else:
                dash_dir = (
                    player_input.move_dir
                    if player_input.move_dir != 0
                    else (
                        1 if player.position.facing == Facing.POS_X else -1
                    )
                )
                
                player.position.vel_x = dash_dir * DASH_SPEED
                player.position.vel_y = 0.0

        if player.position.is_dashing:
            player.position.physics.dash_timer -= 1

            if player.position.physics.dash_timer <= 0:
                player.position.is_dashing = False

            reversing = player_input.reverse_dash and player.mana >= REVERSE_DASH_MANA_COST
            if reversing and player.position.cooldowns.can_reverse_dash:
                player.position.vel_x *= -1
                player.mana -= REVERSE_DASH_MANA_COST
                player.position.cooldowns.cooldown_reverse_dash()

            if player.position.is_dashing and \
                player_input.brake_dash and \
                    player.position.cooldowns.can_brake_dash:
                player.position.is_dashing = False
                player.position.vel_x *= 0.1
                player.position.cooldowns.cooldown_brake_dash()

        player.position.physics.last_dash_pressed = player_input.dash

    def _handle_x_axis(self, player: Player, player_input: PlayerInput):
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

    def _handle_coyote(self, player: Player):
        if player.position.is_grounded:
            player.position.physics.coyote_timer = COYOTE_TICKS
        else:
            if player.position.physics.coyote_timer > 0:
                player.position.physics.coyote_timer -= 1

    def _handle_jump(self, player: Player, player_input: PlayerInput):
        jump_just_pressed = player_input.jump and not player.position.physics.last_jump_pressed

        if jump_just_pressed:
            player.position.physics.jump_buffer_timer = JUMP_BUFFER_TICKS
        elif player.position.physics.jump_buffer_timer > 0:
            player.position.physics.jump_buffer_timer -= 1

        can_jump = player.position.is_grounded or player.position.physics.coyote_timer > 0
        has_jump_buffer = player.position.physics.jump_buffer_timer > 0

        if (jump_just_pressed or has_jump_buffer) and not player_input.duck and can_jump:
            player.position.vel_y = JUMP_FORCE
            player.position.is_grounded = False
            player.position.physics.coyote_timer = 0
            player.position.physics.jump_buffer_timer = 0

        player.position.physics.last_jump_pressed = player_input.jump

    def _handle_hanging(self, player: Player, player_input: PlayerInput):
        will_hang = (
            player_input.hang and
            not player.position.is_grounded and
            player.position.cooldowns.can_hang and
            player.position.physics.hang_timer <= 0 and
            player.mana >= HANG_MANA_COST
        )

        if will_hang:
            player.position.physics.hang_timer = HANG_TICKS
            player.mana -= HANG_MANA_COST
            player.position.cooldowns.cooldown_hang()

    def _handle_gravity(self, player: Player, player_input: PlayerInput):
        player.position.physics.heavy_gravity_timer = max(0, player.position.physics.heavy_gravity_timer - 1)
        player.position.physics.light_gravity_timer = max(0, player.position.physics.light_gravity_timer - 1)

        if player_input.gravity_normal:
            is_of_use = player.position.physics.light_gravity_timer > 0 or player.position.physics.heavy_gravity_timer > 0
            if is_of_use and player.mana >= NORMAL_MANA_COST and player.position.cooldowns.can_normal:
                player.position.physics.light_gravity_timer = 0
                player.position.physics.heavy_gravity_timer = 0
                player.mana -= NORMAL_MANA_COST
                player.position.cooldowns.cooldown_normal()

        can_gravity = player.position.physics.light_gravity_timer == 0 and player.position.physics.heavy_gravity_timer == 0
        if player_input.gravity_heavy:
            if can_gravity and player.mana >= HEAVY_MANA_COST and player.position.cooldowns.can_heavy:
                player.position.physics.heavy_gravity_timer = HEAVY_TICKS
                player.mana -= HEAVY_MANA_COST
                player.position.cooldowns.cooldown_heavy()

        if player_input.gravity_light:
            if can_gravity and player.mana >= LIGHT_MANA_COST and player.position.cooldowns.can_light:
                player.position.physics.light_gravity_timer = LIGHT_TICKS
                player.mana -= LIGHT_MANA_COST
                player.position.cooldowns.cooldown_light()

        gravity_multiplier = (
            LIGHT_SCALAR if player.position.physics.light_gravity_timer > 0
            else (
                HEAVY_SCALAR if player.position.physics.heavy_gravity_timer > 0
                else 1.0
            )
        )

        if not player.position.is_grounded:
            if player.position.physics.hang_timer > 0:
                player.position.physics.hang_timer -= 1
                player.position.vel_y = 0

            else:
                if player.position.vel_y < 0:
                    if not player_input.jump:
                        player.position.vel_y += (
                            GRAVITY_RISE * FAST_FALL_MULTIPLIER * gravity_multiplier
                        )
                    else:
                        player.position.vel_y += GRAVITY_RISE * gravity_multiplier
                else:
                    player.position.vel_y += GRAVITY_FALL * gravity_multiplier

            if player.position.vel_y > TERMINAL_VELOCITY:
                player.position.vel_y = TERMINAL_VELOCITY

    def _decelerate(self, player: Player, current_decel_x: float):
        if player.position.vel_x > 0:
            player.position.vel_x -= current_decel_x
            if player.position.vel_x < 0:
                player.position.vel_x = 0.0

        else:
            player.position.vel_x += current_decel_x
            if player.position.vel_x > 0:
                player.position.vel_x = 0.0

    def _handle_x_collision(self, player: Player, world: World):
        player.position.x += player.position.vel_x
        coll_rect = world.headless.get_collision(player.rect)

        if coll_rect:
            overlap_left = (player.position.x + PLAYER_WIDTH) - coll_rect.left
            overlap_right = coll_rect.right - player.position.x
            overlap_top = (player.position.y + PLAYER_HEIGHT) - coll_rect.top

            stepped_up = False
            if player.position.is_grounded and 0 < overlap_top < STEP_HEIGHT:
                step_amount = overlap_top + 0.02
                player.position.y -= step_amount

                if not world.headless.get_collision(player.rect):
                    stepped_up = True
                else:
                    player.position.y += step_amount

            if not stepped_up:
                if abs(overlap_left) < abs(overlap_right):
                    player.position.x = coll_rect.left - PLAYER_WIDTH
                else:
                    player.position.x = coll_rect.right
                player.position.vel_x = 0

    def _handle_y_collision(self, player: Player, world: World):
        player.position.y += player.position.vel_y
        coll_rect = world.headless.get_collision(player.rect)

        if coll_rect:
            overlap_top = (player.position.y + PLAYER_HEIGHT) - coll_rect.top
            overlap_bottom = coll_rect.bottom - player.position.y

            if abs(overlap_top) < abs(overlap_bottom):
                player.position.y = coll_rect.top - PLAYER_HEIGHT - 0.009
                player.position.is_grounded = True
            else:
                player.position.y = coll_rect.bottom + 0.009
                player.position.is_grounded = False

            player.position.vel_y = 0
        else:
            if player.position.vel_y >= 0:
                ground_rect = Rect(
                    player.position.x,
                    player.position.y + PLAYER_HEIGHT,
                    PLAYER_WIDTH,
                    GROUND_TOLERANCE_PX
                )
                ground_coll = world.headless.get_collision(ground_rect)

                if ground_coll:
                    player.position.is_grounded = True
                    player.position.y = ground_coll.top - PLAYER_HEIGHT
                    player.position.vel_y = 0
                else:
                    player.position.is_grounded = False
            else:
                player.position.is_grounded = False

    def _prepare_attacking(self, player: Player, player_input: PlayerInput):
        if player_input.parry and player.position.cooldowns.can_parry and player.mana >= PARRY_MANA_COST:
            player.position.physics.invulnerable_timer = PARRY_TICKS
            player.position.cooldowns.cooldown_parry()

        player.position.physics.invulnerable_timer = max(0, player.position.physics.invulnerable_timer - 1)
        player.position.physics.stun_timer = max(0, player.position.physics.stun_timer - 1)
        player.position.combo.timer = max(0, player.position.combo.timer - 1)

    def _handle_push(self, player: Player, player_input: PlayerInput, others: list[Player]):
        if player_input.push and player.position.cooldowns.can_push:
            success = False

            for other in others:
                if other.position.physics.invulnerable_timer > 0:
                    continue

                dx = other.position.x - player.position.x
                dy = abs(other.position.y - player.position.y)

                if abs(dx) > PUSH_RANGE or dy > PUSH_VERTICAL_TOLERANCE:
                    continue

                direction = 1 if dx >= 0 else -1
                other.position.vel_x += direction * PUSH_FORCE_X
                other.position.vel_y += PUSH_FORCE_Y
                other.position.is_grounded = False
                other.position.physics.invulnerable_timer = PUSH_IFRAMES

                other.position.combo.hits = 0
                other.position.combo.timer = 0
                other.position.combo.broken = True

                success = True

            if success:
                player.position.cooldowns.cooldown_push()

    def _handle_stomp(self, player: Player, player_input: PlayerInput, others: list[Player]):
        if player_input.stomp and player.position.is_grounded and player.position.cooldowns.can_stomp:
            success = False

            for other in others:
                if other.position.physics.invulnerable_timer > 0:
                    continue

                dx = other.position.x - player.position.x
                dy = other.position.y - player.position.y
                dist_sq = dx**2 + dy**2

                if dist_sq > (STOMP_RANGE ** 2):
                    continue

                dist = dist_sq ** 0.5
                nx = dx / dist
                ny = min(-0.2, dy / dist)  # bias upward

                strength = 1 - (dist / STOMP_RANGE)

                other.position.is_grounded = False
                other.position.physics.invulnerable_timer = STOMP_IFRAMES

                other.position.combo.hits = 0
                other.position.combo.timer = 0
                other.position.combo.broken = True

                other.position.vel_x += nx * STOMP_KNOCKBACK_X * strength
                other.position.vel_y += ny * STOMP_KNOCKBACK_Y * strength

                other.health = max(0, other.health - STOMP_DAMAGE)

                success = True

            if success:
                player.position.cooldowns.cooldown_stomp()

    def _handle_punch(self, player: Player, player_input: PlayerInput, others: list[Player]):
        if player_input.punch and player.position.cooldowns.can_punch:
            success = False

            for other in others:
                if other.position.physics.invulnerable_timer > 0:
                    continue

                dx = other.position.x - player.position.x
                dy = other.position.y - player.position.y
                dist_sq = dx**2 + dy**2

                if dist_sq > (PUNCH_RANGE ** 2):
                    continue

                dist = dist_sq ** 0.5

                other.health = max(0, other.health - PUNCH_DAMAGE)
                other.position.physics.invulnerable_timer = PUNCH_IFRAMES

                other.position.combo.hits = 0
                other.position.combo.timer = 0
                other.position.combo.broken = True

                player.position.combo.hits += 1
                player.position.combo.timer = PUNCH_COMBO_WINDOW_TICKS

                if player.position.combo.hits >= PUNCHES_TO_KNOCKDOWN:
                    other.position.physics.stun_timer = PUNCH_STUN_TICKS
                    other.position.vel_x += (dx / max(dist, 0.0001)) * PUNCH_KNOCKDOWN_KB_X
                    other.position.vel_y += PUNCH_KNOCKDOWN_KB_Y
                    other.position.is_grounded = False

                recoil_dir = -1 if dx > 0 else 1
                player.position.vel_x += recoil_dir * PUNCH_RECOIL_X
                player.position.vel_y += PUNCH_RECOIL_Y

                success = True

            if success:
                player.position.cooldowns.cooldown_punch()

