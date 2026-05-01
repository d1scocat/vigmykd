from typing import Tuple


class TextureRef:
    def __init__(self, sheet: int, tile: Tuple[int, int]):
        self.sheet = sheet
        self.tile = tile
