from dataclasses import dataclass

from event.model import Event

from google.protobuf.message import Message


@dataclass
class UDPAckEvent(Event):
    msg_id: int
    ok: bool

    def get_name(self) -> str:
        return "UDPAckEvent"

@dataclass
class UDPReceivedEvent(Event):
    message_type: type[Message]
    message: Message
    envelope: Message

    def get_name(self) -> str:
        return "UDPReceivedEvent"