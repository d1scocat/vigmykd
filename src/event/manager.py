import logging
import threading
import queue

from event.model import Event
from typing import Callable
from collections import defaultdict


class EventManager:
    """
    Pygame is not thread-safe, apparently.
    This event management system tries to work alongside that fact
    """

    listeners: dict[type[Event], list[tuple[int, Callable[[Event], None]]]]
    latest_id: int

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.listeners = defaultdict(list)
        self.latest_id = 0

        self._lock = threading.Lock()
        self._queue: queue.Queue[Event] = queue.Queue()

    def register_listener(self, event_type: type[Event], func: Callable) -> int:
        with self._lock:
            self.latest_id += 1
            self.listeners[event_type].append((self.latest_id, func))
            return self.latest_id

    def unregister_listener(self, target_id: int):
        with self._lock:
            for listeners in self.listeners.values():
                # otherwise it'll complain during iteration
                listeners[:] = [(lid, func) for lid, func in listeners if lid != target_id]

    def invoke_event(self, event: Event):
        self._queue.put(event)

    def push(self):
        try:
            while True:
                event = self._queue.get_nowait()
                with self._lock:
                    callbacks = [func for _, func in self.listeners.get(type(event), [])]
                for callback in callbacks:
                    try:
                        callback(event)
                    except Exception as ex:
                        name = getattr(callback, "__name__", type(callback).__name__)
                        self.logger.warning("Unhandled exception at event callback:\n"
                                            f"- Event type {event} encountered an exception"
                                            f" while being intercepted by {name}:\n{str(ex)}",
                                            exc_info=True)

        except queue.Empty:
            pass
