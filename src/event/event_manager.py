from event.event import Event
from typing import Callable, Dict, Tuple, List
from collections import defaultdict


class EventManager:
    listeners: Dict[Event, List[Tuple[int, Callable[[Event], None]]]]
    latest_id: int

    def __init__(self):
        self.listeners = defaultdict(list)
        self.latest_id = 0

    def register_listener(self, event_type: Event, func: Callable) -> int:
        self.latest_id += 1
        self.listeners[event_type].append((self.latest_id, func))
        return self.latest_id

    def unregister_listener(self, target_id: int):
        for event, listeners in self.listeners.items():
            self.listeners[event] = [
                (id, func) for (id, func) in listeners if id != target_id
            ]

    def invoke_event(self, event_type: Event):
        listeners = self.listeners[event_type]
        for _, func in listeners:
            func(event_type)
