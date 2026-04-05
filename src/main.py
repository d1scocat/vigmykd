import pygame
from log import setup as log_setup
from game import Game
from context import GameContext
from pathlib import Path


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

game = Game(
    ctx=ctx,
    screen=screen
)

while running:
    dt = clock.tick(60) / 1000  # seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game.handle_input(dt)
    game.render()

    pygame.display.flip()
