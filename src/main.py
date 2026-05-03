import pygame
from pathlib import Path

from context import GameContext
from game.game import Game
from log import setup as log_setup
from textures.loader import load_sheets

from settings import TPS_DELTA, \
    MAX_TICKS_PER_FRAME as MAX_TICKS

import registry

# Import for registration
# from controller.consumers import *
# from controller.mutators import *
# from view.adapter import *

from event import EventManager


pygame.init()

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

screen_size = (screen_width - 300, screen_height - 300)

# debug purposes configuration
screen = pygame.display.set_mode(screen_size)

pygame.display.set_caption("vigmykd")

log_setup()

# Game loop
running = True
clock = pygame.time.Clock()

ctx = GameContext(
    assets_path=Path("assets"),
    cfg_path=Path("cfg"),
    screen_size=screen_size
)

load_sheets(ctx, ctx.texture_manager)

registry.registries.init_all()

event_manager = EventManager()

game = Game(
    ctx=ctx,
    screen=screen,
    event_manager=event_manager
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
