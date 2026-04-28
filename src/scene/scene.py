from controller.input_model import Mutation
from view import Renderer
from view.system import ViewSystem

from abc import ABC, abstractmethod
from typing import List


class Scene(ABC):
    @abstractmethod
    def tick(self, input_mutations: List[Mutation]):
        pass

    @abstractmethod
    def render(self, view: Renderer, view_system: ViewSystem):
        pass
