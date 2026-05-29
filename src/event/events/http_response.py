import uuid

from dataclasses import dataclass
from typing import Any, Dict

from event.model import Event


@dataclass
class HTTPResponseEvent(Event):
    request_id: uuid.UUID
    endpoint: str
    method: str
    successful: bool
    status_code: int
    payload: Dict[str, Any]
    exc_info: str | None = None

    @property
    def success(self):
        return self.successful and self.status_code < 400

    def get_name(self) -> str:
        return "HTTPResponseEvent"
