from typing import Dict, List, Tuple
import pygame


class TextureManager:
    spritesheets: Dict[int, List[List[pygame.Surface]]]

    def __init__(self):
        self.spritesheets = {}

    def add_spritesheet(self, id: int, sheet: List[List[pygame.Surface]]):
        self.spritesheets[id] = sheet

    def lookup_tile(self, sheet_id: int, pos: Tuple[int, int]) -> pygame.Surface | None:
        sheet = self.spritesheets.get(sheet_id)
        assert sheet is not None and sheet[0], f"Spritesheet {sheet_id} not found"

        x, y = pos

        if 0 <= y < len(sheet) and 0 <= x < len(sheet[0]):
            return sheet[y][x]
        return None
