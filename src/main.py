import logging

from pathlib import Path

import pygame

import registry

from config import load_config
from context import GameContext
from event import EventManager
from game.game import Game
from log import setup as log_setup
from network import ApiClient
from textures.loader import load_sheets

from settings import TPS_DELTA, \
    MAX_TICKS_PER_FRAME as MAX_TICKS


# ===== INITIALIZING SCREEN AND PYGAME ===== #
pygame.init()

info = pygame.display.Info()

screen_width = info.current_w
screen_height = info.current_h
screen_size = (screen_width - 300, screen_height - 300)
screen = pygame.display.set_mode(screen_size)

pygame.display.set_caption("vigmykd")

pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

# ===== INITIALIZING LOGGING ===== #
log_setup()
logger = logging.getLogger("vigmykd")

# ===== INITIALIZING GLOBALLY SHARED DATA ===== #
CFG_PATH = Path("cfg")
ASSETS_PATH = Path("assets")

cfg = load_config(CFG_PATH / "config.json")
event_manager = EventManager(logger=logger)
api_client = ApiClient(
    base_url=cfg.server,
    event_manager=event_manager
)

ctx = GameContext(
    logger=logger,
    event_manager=event_manager,
    assets_path=ASSETS_PATH,
    cfg_path=CFG_PATH,
    cfg=cfg,
    client=api_client,
    screen_size=screen_size
)

game = Game(
    ctx=ctx,
    screen=screen,
    event_manager=event_manager
)

load_sheets(ctx, ctx.texture_manager)

registry.registries.init_all()

# ===== LISTENERS ===== #
# TODO: extract this somewhere
from event.events import HTTPResponseEvent
from listeners import LoginListener
listeners = [
    (LoginListener(ctx), HTTPResponseEvent)
]

for (listener, type) in listeners:
    listener.sub(type, event_manager)

# ===== GAME LOOP ===== #
running = True
clock = pygame.time.Clock()

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
