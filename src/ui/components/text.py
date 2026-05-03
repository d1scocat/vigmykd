from abc import ABC, abstractmethod
from typing import Tuple


class UIText:
    def __init__(self, i18n: str, font: str, size: int, color: Tuple[int, int, int]):
        self.i18n = i18n
        self.font = font
        self.size = size
        self.color = color


class UITextHolder(ABC):
    @property
    @abstractmethod
    def text(self) -> UIText | None:
        pass
