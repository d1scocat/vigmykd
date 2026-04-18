from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from view.renderable import Renderable


T = TypeVar("T")


class ViewAdapter(ABC, Generic[T]):
    @abstractmethod
    def create(self, object: T, *args, **kwargs) -> Renderable:
        pass

    @abstractmethod
    def update(self, object: T, renderable: Renderable):
        pass
