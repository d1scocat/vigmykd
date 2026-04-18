import pygame
import math
from pathlib import Path

from context import GameContext
from game import Game
from log import setup as log_setup
from textures.load_sheets import load_sheets

from settings import TPS_DELTA, \
    MAX_TICKS_PER_FRAME as MAX_TICKS


pygame.init()

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# debug purposes configuration
screen = pygame.display.set_mode(
    (screen_width - 100, screen_height - 100)  # , pygame.FULLSCREEN
)

pygame.display.set_caption("vigmykd")

log_setup()

# Game loop
running = True
clock = pygame.time.Clock()

ctx = GameContext(
    assets_path=Path("assets")
)

load_sheets(ctx, ctx.texture_manager)

game = Game(
    ctx=ctx,
    screen=screen
)

# fps/tps separation
accumulator: float = 0.0

while running:
    frame_dt = clock.tick(60) / 1000
    accumulator += frame_dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            game.handle_input_prep(event)

    ticks_simulated = 0
    while accumulator >= TPS_DELTA and ticks_simulated < MAX_TICKS:
        game.tick()
        accumulator -= TPS_DELTA
        ticks_simulated += 1

        # account for marginally small floating point drifting
        # nvm might be buggy
        # if accumulator < math.pow(10, -4):
        #    accumulator = 0.0

    game.render()

    pygame.display.flip()
