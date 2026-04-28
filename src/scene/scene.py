from view import Renderer
from view.system import ViewSystem

from abc import ABC, abstractmethod


class Scene(ABC):
    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def render(self, view: Renderer, view_system: ViewSystem):
        pass
