from context import GameContext
from ui.components.page import UIPage
from ui.deserializer import deserialize_into_ui
from view import Renderer
from view.system import ViewSystem

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Self

import json

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
    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        """
            Returns: True if the event is intercepted by the scene and should not
            be handled by the central input handler (e.g. textarea handling).
        """
        pass

    @abstractmethod
    def render(self, view: Renderer, view_system: ViewSystem):
        pass

    @abstractmethod
    def find_action(self, action_name: str) -> Callable[['Scene', GameContext], Any] | None:
        pass

    @property
    @abstractmethod
    def page(self) -> UIPage:
        pass

    def get_ui(self, file_path: Path) -> UIPage:
        data = json.loads(file_path.read_text())
        return deserialize_into_ui(data)
