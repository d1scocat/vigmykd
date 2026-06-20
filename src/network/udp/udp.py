import errno
import time

from collections import deque
from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Callable, Protocol, runtime_checkable

from event import EventManager
from event.events import UDPAckEvent, UDPReceivedEvent
from settings import NETWORK_TICK_LIMIT
from network.udp.config import GameServerConfig

from generated.proto.v1 import packet_pb2 as packet_pb2

from google.protobuf.message import Message, DecodeError


@runtime_checkable
class HasSerializeToString(Protocol):
    def SerializeToString(self) -> bytes: ...


@dataclass
class _WaitingAck:
    message: bytes
    addr: tuple[str, int]
    last_sent: float = field(default_factory=time.monotonic)
    attempts: int = 0


class GameServerClient:
    def __init__(self, event_manager: EventManager, logger: Logger, cfg_path: Path):
        self.logger = logger
        self.event_manager = event_manager

        self._perform_on_ack = {}
        self._waiting_ack = {}

        # self.incoming = deque(maxlen=2048)
        self.outgoing = deque(maxlen=2048)

        self.config = GameServerConfig(logger, cfg_path)

        self.running = True
        self.sock = self._bind_socket()

        self._last_unacked_check = time.monotonic()

    def _bind_socket(self) -> socket:
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setblocking(False)

        self.bound_port: int
        start_port = self.config.port
        max_port = start_port + self.config.scan_for_max

        for port in range(start_port, max_port + 1):
            try:
                sock.bind(('0.0.0.0', port))
                self.logger.info("Internal socket listening on 0.0.0.0:%d", port)
                self.bound_port = port
                return sock
            except OSError as ex:
                if ex.errno == errno.EADDRINUSE:
                    continue
                raise  # Unexpected path

        sock.close()
        raise RuntimeError(f"No free port for socket in range [{start_port}; {max_port}]")

    def enqueue(
        self,
        value: bytes | HasSerializeToString,
        msg_id: int,
        needs_ack: bool = False,
        callback: Callable[[bool], None] | None = None
    ):
        # Whatever we receive!
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, HasSerializeToString):
            data = value.SerializeToString()
        else:
            self.logger.warning("Cannot send bad packet: %r", value)
            return
        
        self.outgoing.append(data)
        if needs_ack:
            if callback is not None:
                self._perform_on_ack[msg_id] = callback
            self._waiting_ack[msg_id] = _WaitingAck(
                message=data,
                addr=(self.config.server_addr, self.config.server_port)
            )

    def pump(self):
        if not self.running:
            return

        start = time.perf_counter()

        self._recv(start)
        self._send(start)
        self._send_unacked()

    def shutdown(self):
        self.running = False
        self.sock.close()

    def _recv(self, start_time):
        deadline = start_time + NETWORK_TICK_LIMIT * 0.4
        while time.perf_counter() < deadline:
            try:
                packet, _ = self.sock.recvfrom(2048)
                self.logger.debug("Got packet of size %d", len(packet))
            except BlockingIOError:
                return
            except OSError:
                self.logger.exception("Socket recv failed")
                continue
            except Exception:
                self.logger.exception(f"recv_worker crashed while processing packet")

            try:
                envelope = packet_pb2.Envelope()
                envelope.ParseFromString(packet)
            except DecodeError:
                self.logger.warning("Received malformed packet from server")
                continue

            self._check_ack(envelope)
            self._invoke_event(envelope)
            # self.incoming.append(packet)

    def _send(self, start_time):
        deadline = start_time + NETWORK_TICK_LIMIT * 0.4
        while time.perf_counter() < deadline:
            if not self.outgoing:
                break

            data = self.outgoing[0]
            try:
                self.sock.sendto(data, (self.config.server_addr, self.config.server_port))
                self.outgoing.popleft()
            except BlockingIOError:
                break
            except OSError:
                self.outgoing.popleft()
                self.logger.exception("Packet send failed")

    def _send_unacked(self):
        now = time.monotonic()
        if now - self._last_unacked_check < self.config.reack_interval:
            return

        self._last_unacked_check = now

        expired = []

        for m_key, message in list(self._waiting_ack.items()):
            data = message.message
            client = message.addr
            last_sent = message.last_sent
            attempts = message.attempts

            if attempts >= self.config.max_ack_attempts:
                expired.append(m_key)
                continue

            if now - last_sent > self.config.reack_interval:
                try:
                    self.sock.sendto(data, client)
                except BlockingIOError:
                    break
                except Exception:
                    self.logger.warning("Could not retransmit ack-waiting message to server")
                else:
                    message.last_sent = now
                    message.attempts += 1

        for item in expired:
            self.logger.debug("Packet %s expired after %s retries",
                                item, self.config.max_ack_attempts)
            self._waiting_ack.pop(item, None)

    def _check_ack(self, envelope: packet_pb2.Envelope):
        if envelope.WhichOneof("payload") != "packet":
            return

        packet = envelope.packet
        if packet.WhichOneof("payload") != "server_to_client":
            return

        stc = packet.server_to_client
        if stc.WhichOneof("payload") != "ack":
            return

        ack = stc.ack
        mid = ack.acknowledged_msg_id

        self.event_manager.invoke_event(UDPAckEvent(mid, ack.ok))

        self._waiting_ack.pop(mid, None)

        callback = self._perform_on_ack.pop(mid, None)
        if callback is not None:
            try:
                callback(ack.ok)
            except Exception:
                self.logger.exception("Exception handing acking callback for msg_id %d", mid)

    def _invoke_event(self, envelope: packet_pb2.Envelope):
        inner = self._innermost_message(envelope)
        msg_type = type(inner)

        self.event_manager.invoke_event(UDPReceivedEvent(msg_type, inner, envelope))

    def _innermost_message(self, message: Message):
        while True:
            try:
                oneof = message.WhichOneof("payload")
                if oneof is None:
                    return message
                message = getattr(message, oneof)
            except ValueError:  # no 'payload'
                return message
