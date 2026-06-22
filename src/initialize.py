import pygame

import logging

# registry-related imports
import registry
from controller.consumers.input_consumer import *
from controller.consumers.movement_consumer import *
from controller.mutators.movement import *
from view.adapter.player import *

# listener-related imports
from event.events import HTTPResponseEvent
from listeners import LoginListener, PubkeyListener

from game.game import Game
from log import setup as log_setup    


def init_with_screen() -> tuple[pygame.Surface, tuple[int, int]]:
    pygame.init()

    info = pygame.display.Info()

    screen_width = info.current_w
    screen_height = info.current_h
    screen_size = (screen_width - 100, screen_height - 100)

    pygame.display.set_caption("vigmykd")

    screen = pygame.display.set_mode(screen_size)

    pygame.scrap.init()
    pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

    return (screen, screen_size)


def init_logger() -> logging.Logger:
    log_setup()
    return logging.getLogger("vigmykd")


def init_registries():
    registry.registries.init_all()


def init_listeners(ctx: GameContext, game: Game):
    listeners = [
        (LoginListener(ctx), HTTPResponseEvent),
        (PubkeyListener(ctx, game.model), HTTPResponseEvent)
    ]

    for (listener, type) in listeners:
        listener.sub(type, ctx.event_manager)
