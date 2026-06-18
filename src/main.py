import logging

from pathlib import Path

import pygame

import registry

from config import load_config
from context import GameContext
from event import EventManager
from event.events import GameQuitEvent
from game.game import Game
from log import setup as log_setup
from network import ApiClient, GameServerClient
from textures.loader import load_sheets

from settings import TPS_DELTA, \
    MAX_TICKS_PER_FRAME as MAX_TICKS


# ===== INITIALIZING SCREEN AND PYGAME ===== #
pygame.init()
running = True


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
registry.registries.init_all()

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
# TODO: extract this somewhere
from event.events import HTTPResponseEvent
from listeners import LoginListener, PubkeyListener

listeners = [
    (LoginListener(ctx), HTTPResponseEvent),
    (PubkeyListener(ctx, game.model), HTTPResponseEvent)
]

for (listener, type) in listeners:
    listener.sub(type, event_manager)

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
