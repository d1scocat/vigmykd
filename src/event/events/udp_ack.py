from dataclasses import dataclass

from event.model import Event


@dataclass
class UDPAckEvent(Event):
    msg_id: int
    ok: bool

    def get_name(self) -> str:
        return "UDPAckEvent"