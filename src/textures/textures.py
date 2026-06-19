import pygame


class TextureManager:
    spritesheets: dict[int, list[list[pygame.Surface]]]

    def __init__(self):
        self.spritesheets = {}

    def add_spritesheet(self, sheet_id: int, sheet: list[list[pygame.Surface]]):
        self.spritesheets[sheet_id] = sheet

    def lookup_tile(self, sheet_id: int, pos: tuple[int, int]) -> pygame.Surface | None:
        sheet = self.spritesheets.get(sheet_id)
        if sheet is None or not sheet[0]:
            raise ValueError(f"Spritesheet {sheet_id} not found")

        x, y = pos

        if 0 <= y < len(sheet) and 0 <= x < len(sheet[0]):
            return sheet[y][x]
        return None
