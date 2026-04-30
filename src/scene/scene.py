from view import Renderer
from view.system import ViewSystem

from abc import ABC, abstractmethod

import pygame


class Scene(ABC):
    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_exit(self):
        pass

    @abstractmethod
    def handle_pygame_event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def render(self, view: Renderer, view_system: ViewSystem):
        pass
