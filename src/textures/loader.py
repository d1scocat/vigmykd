import json
import pygame

from textures import TextureManager
from context import GameContext

from pathlib import Path
from typing import Any


def load_spritesheet(
    path: Path,
    tile_size: tuple[int, int],
    grid_size: tuple[int, int],
    offset: tuple[int, int] = (0, 0),
    spacing: tuple[int, int] = (0, 0),
) -> list[list[pygame.Surface]]:
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


def load_sheets(ctx: GameContext, manager: TextureManager):
    sheets_path = ctx.sheets_path
    sheets_file = sheets_path / "sheets.json"
    sheets: list[dict[str, Any]] = json.loads(sheets_file.read_text())

    for sheet in sheets:
        id = sheet["id"]
        path = sheets_path / sheet["path"]
        tile_size = tuple(sheet["tile-size"])
        grid_size = tuple(sheet["grid-size"])

        offset = tuple(sheet.get("offset", [0, 0]))
        spacing = tuple(sheet.get("spacing", [0, 0]))

        manager.add_spritesheet(
            id=id,
            sheet=load_spritesheet(
                path=path,
                tile_size=tile_size,
                grid_size=grid_size,
                offset=offset,
                spacing=spacing
            )
        )
