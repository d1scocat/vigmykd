from dataclasses import dataclass

from event.model import Event


@dataclass
class GameQuitEvent(Event):
    def get_name(self) -> str:
        return "GameQuitEvent"
