import pygame
from pathlib import Path
from typing import List, Tuple


def load_spritesheet(
    path: Path,
    tile_size: Tuple[int, int],
    grid_size: Tuple[int, int],
    offset: Tuple[int, int] = (0, 0),
    spacing: Tuple[int, int] = (0, 0),
) -> List[List[pygame.Surface]]:
    sheet = pygame.image.load(path).convert_alpha()

    tile_w, tile_h = tile_size
    cols, rows = grid_size
    offset_x, offset_y = offset
    spacing_x, spacing_y = spacing

    sprites = []

    for y in range(rows):
        row = []
        for x in range(cols):
            rect = pygame.Rect(
                offset_x + x * (tile_w + spacing_x),
                offset_y + y * (tile_h + spacing_y),
                tile_w,
                tile_h
            )
            sprite = sheet.subsurface(rect).copy()
            row.append(sprite)

        sprites.append(row)

    return sprites
