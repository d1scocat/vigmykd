from abc import ABC, abstractmethod

from game.game import Game


class Scene(ABC):
    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def render(self, game: Game):
        pass
