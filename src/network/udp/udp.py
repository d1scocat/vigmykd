import errno
import time
import queue

from logging import Logger
from pathlib import Path
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Protocol, runtime_checkable

from event import EventManager
from event.events import UDPAckEvent
from settings import NETWORK_TICK_LIMIT
from network.udp.config import GameServerConfig

from generated.proto.v1 import packet_pb2 as packet_pb2


@runtime_checkable
class HasSerializeToString(Protocol):
    def SerializeToString(self) -> bytes: ...


class GameServerClient:
    def __init__(self, event_manager: EventManager, logger: Logger, cfg_path: Path):
        self.logger = logger
        self.event_manager = event_manager

        self._waits_ack = {}

        self.incoming = queue.Queue(maxsize=2048)
        self.outgoing = queue.Queue(maxsize=2048)

        self.config = GameServerConfig(logger, cfg_path)

        self.running = True
        self.sock = self._bind_socket()

    def _bind_socket(self) -> socket:
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setblocking(False)

        self.bound_port: int
        start_port = self.config.port
        max_port = start_port + self.config.scan_for_max

        for port in range(start_port, max_port + 1):
            try:
                sock.bind(('0.0.0.0', port))
                self.logger.info(f"Internal socket listening on 0.0.0.0:{port}")
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
        callback = None
    ):
        # Whatever we receive!
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, HasSerializeToString):
            data = value.SerializeToString()
        else:
            self.logger.warning(f"Cannot send bad packet: {value!r}")
            return
        
        self._push_drop_oldest(self.outgoing, data)
        if needs_ack and callback is not None:
            self._waits_ack[msg_id] = callback

    def pump(self):
        if not self.running:
            return

        start = time.perf_counter()

        self._recv(start)
        self._send(start)

    def shutdown(self):
        self.running = False
        self.sock.close()

    def _recv(self, start_time):
        deadline = start_time + NETWORK_TICK_LIMIT * 0.5
        while time.perf_counter() < deadline:
            try:
                packet, _ = self.sock.recvfrom(2048)
                self._check_ack(packet)
            except BlockingIOError:
                return

            self._push_drop_oldest(self.incoming, packet)

    def _send(self, start_time):
        deadline = start_time + NETWORK_TICK_LIMIT * 0.5
        while time.perf_counter() < deadline:
            try:
                data = self.outgoing.get_nowait()
                self.sock.sendto(data, (self.config.server_addr, self.config.server_port))
            except BlockingIOError:
                pass
            except OSError:
                self.logger.exception("Packet send failed")
            except queue.Empty:
                break

    def _check_ack(self, data):
        envelope = packet_pb2.Envelope()
        envelope.ParseFromString(data)
        if envelope.WhichOneof("payload") != "packet":
            return

        packet = envelope.packet
        if packet.WhichOneof("payload") != "server_to_client":
            return

        stc = packet.server_to_client
        if stc.WhichOneof("payload") != "ack":
            return

        ack = stc.ack

        self.event_manager.invoke_event(UDPAckEvent(ack.acknowledged_msg_id, ack.ok))

        callback = self._waits_ack.pop(ack.acknowledged_msg_id, None)
        if callback is not None:
            callback(ack.ok)

    def _push_drop_oldest(self, q: queue.Queue[bytes], item: bytes) -> None:
        try:
            q.put_nowait(item)
        except queue.Full:
            try:
                q.get_nowait()
                q.put_nowait(item)
            except queue.Empty:
                pass
