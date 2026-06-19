import json
import pygame

from textures import TextureManager

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


def load_sheets(
    ctx: 'context.GameContext',
    manager: TextureManager,
    path_to_sheets: Path | None = None,
    sheets_file_name: str = "sheets.json"
):
    sheets_path = path_to_sheets or ctx.sheets_path
    sheets_file = sheets_path / sheets_file_name
    sheets: list[dict[str, Any]] = json.loads(sheets_file.read_text())

    for sheet in sheets:
        load_sheet(sheet, sheets_path, manager)


def load_sheet(
    sheet: dict[str, Any],
    parent_path: Path,
    manager: TextureManager
):
    sheet_id = sheet["id"]
    path = parent_path / sheet["path"]
    tile_size = tuple(sheet["tile-size"])
    grid_size = tuple(sheet["grid-size"])

    offset = tuple(sheet.get("offset", [0, 0]))
    spacing = tuple(sheet.get("spacing", [0, 0]))

    manager.add_spritesheet(
        sheet_id=sheet_id,
        sheet=load_spritesheet(
            path=path,
            tile_size=tile_size,
            grid_size=grid_size,
            offset=offset,
            spacing=spacing
        )
    )


def texture_packer_to_spritesheet(sheet_id: int, file: Path, spritesheet: Path) -> dict[str, Any]:
    """
    Assumes uniform size of assets, with no padding, and no extra nesting
    of spritesheet directory
    """

    data = json.loads(file.read_text())

    size = data["meta"]["size"]
    w, h = size["w"], size["h"]

    frames = data["frames"]

    first_frame = frames[0]["frame"]
    tile_w, tile_h = first_frame["w"], first_frame["h"]

    last_frame = frames[-1]["frame"]
    grid_w, grid_h = (last_frame["x"] // tile_w) + 1, (last_frame["y"] // tile_h) + 1

    return {
        "id": sheet_id,
        "path": spritesheet.name,
        "tile-size": (tile_w, tile_h),
        "grid-size": (grid_w, grid_h)
    }
