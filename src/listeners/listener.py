from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from event import Event, EventManager


T = TypeVar('T', bound=Event)


class Listener(ABC, Generic[T]):
    def __init__(self):
        self._lid: int | None = None

    def sub(self, event_type: type[T], event_manager: EventManager):
        if self._lid is not None:
            return
        self._lid = event_manager.register_listener(event_type, self.callback)

    def unsub(self, event_manager: EventManager):
        if self._lid is not None:
            event_manager.unregister_listener(self._lid)
            self._lid = None

    @property
    def is_subscribed(self) -> bool:
        return self._lid is not None

    @abstractmethod
    def callback(self, event: T):
        pass
