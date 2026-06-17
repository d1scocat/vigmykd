from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from game.model.state import GameState
from view.renderable import Renderable


T = TypeVar("T")


class ViewAdapter(ABC, Generic[T]):
    @abstractmethod
    def create(self, object: T, *args, **kwargs) -> Renderable:
        pass

    @abstractmethod
    def update(
        self,
        object: T,
        renderable: Renderable,
        model: GameState,
        current_render_tick: float
    ):
        pass
