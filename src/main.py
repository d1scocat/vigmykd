import logging

from pathlib import Path

import pygame

from config import load_config
from context import GameContext
from event import EventManager
from event.events import GameQuitEvent
from game.game import Game
from initialize import init_logger, init_with_screen, init_registries, init_listeners
from network import ApiClient, GameServerClient
from sound import SoundManager
from textures.loader import load_sheets

from settings import TPS_DELTA, \
    MAX_TICKS_PER_FRAME as MAX_TICKS, \
    CFG_PATH, \
    ASSETS_PATH


# ===== INITIALIZING SCREEN AND PYGAME ===== #
logger = init_logger()
init_registries()

screen, screen_size = init_with_screen()

running = True

# ===== INITIALIZING GLOBALLY SHARED DATA ===== #
cfg = load_config(CFG_PATH / "config.json")

event_manager = EventManager(logger=logger)

sound_manager = SoundManager()

api_client = ApiClient(
    base_url=cfg.server,
    event_manager=event_manager
)

ctx = GameContext(
    logger=logger,
    event_manager=event_manager,
    sound_manager=sound_manager,
    assets_path=ASSETS_PATH,
    cfg_path=CFG_PATH,
    cfg=cfg,
    client=api_client,
    screen_size=screen_size
)

server_client = GameServerClient(
    logger=logger,
    event_manager=event_manager,
    cfg_path=CFG_PATH
)

game = Game(
    ctx=ctx,
    screen=screen,
    event_manager=event_manager,
    server_client=server_client
)

load_sheets(ctx, ctx.texture_manager)

# ===== Requesting key ===== #
api_client.get("/key/public")


# Auxiliary function, subscribes to GameQuitEvent for graceful shutdowns
def _aux_stop_running(_: GameQuitEvent):
    global running
    running = False


# ===== LISTENERS ===== #
init_listeners(ctx, game)

event_manager.register_listener(GameQuitEvent, _aux_stop_running)

# ===== GAME LOOP ===== #
clock = pygame.time.Clock()

# fps/tps separation
accumulator: float = 0.0

while running:
    frame_dt = clock.tick(60) / 1000
    accumulator += frame_dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            event_manager.invoke_event(GameQuitEvent())
        else:
            game.handle_input_prep(event)

    ticks_simulated = 0
    while accumulator >= TPS_DELTA and ticks_simulated < MAX_TICKS:
        game.tick()
        accumulator -= TPS_DELTA
        ticks_simulated += 1

    render_alpha = accumulator / TPS_DELTA  # interpolation alpha
    game.render(render_alpha)

    pygame.display.flip()
