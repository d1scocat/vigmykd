from generated.proto.v1 import packet_pb2 as packet_pb2

from controller.input_model import PlayerInput

from typing import Any, overload


class Packets:
    _id = 0

    @staticmethod
    def get_next_id() -> int:
        # By my own convention, the server gets message IDs in the range
        # (1'000'000'000-2'000'000'000]. The client gets [1-1'000'000'000]
        Packets._id += 1
        return Packets._id

    @staticmethod
    def matchmaking_quit(
        msg_id: int | None = None
    ):
        """`envelope()` a packet before sending!"""
        if msg_id is None:
            msg_id = Packets.get_next_id()

        packet = packet_pb2.Packet()
        packet.msg_id = msg_id

        packet.client_to_server.matchmaking_quit.SetInParent()

        return packet

    @staticmethod
    def matchmaking_enter(
        match_id: str,
        join_token: str,
        msg_id: int | None = None
    ):
        """`envelope()` a packet before sending!"""
        if msg_id is None:
            msg_id = Packets.get_next_id()

        packet = packet_pb2.Packet()
        packet.msg_id = msg_id

        packet.client_to_server.matchmaking_enter.match_id = match_id
        packet.client_to_server.matchmaking_enter.join_token = join_token

        return packet

    @staticmethod
    def request_match_info(
        msg_id: int | None = None
    ):
        """`envelope()` a packet before sending!"""
        if msg_id is None:
            msg_id = Packets.get_next_id()

        packet = packet_pb2.Packet()
        packet.msg_id = msg_id

        packet.client_to_server.request_match_info.SetInParent()

        return packet

    @staticmethod
    def player_move_state(
        player_input: dict[str, Any],
        client_tick: int,
        msg_id: int | None = None
    ):
        """`envelope()` a packet before sending!"""
        if msg_id is None:
            msg_id = Packets.get_next_id()

        packet = packet_pb2.Packet()
        packet.msg_id = msg_id

        move_state = packet_pb2.PlayerMoveState()
        move_state.move_dir = player_input.get("move_dir", 0)
        move_state.duck = player_input.get("duck", False)
        move_state.jump = player_input.get("jump", False)
        move_state.dash = player_input.get("dash", False)

        move_state.client_tick = client_tick

        packet.client_to_server.player_move_state.CopyFrom(move_state)

        return packet

    @staticmethod
    def ack(
        msg_id: int,
        ok: bool
    ):
        """`envelope()` a packet before sending!"""
        packet = packet_pb2.Packet()
        packet.msg_id = Packets.get_next_id()
        packet.client_to_server.ack.acknowledged_msg_id = msg_id
        packet.client_to_server.ack.ok = ok

        return packet

    @staticmethod
    @overload
    def envelope(
        payload: packet_pb2.Packet,
    ) -> packet_pb2.Envelope:
        ...

    @staticmethod
    @overload
    def envelope(
        payload: packet_pb2.SignedPacket,
    ) -> packet_pb2.Envelope:
        ...

    @staticmethod
    def envelope(payload):
        env = packet_pb2.Envelope()

        if isinstance(payload, packet_pb2.Packet):
            env.packet.CopyFrom(payload)
        elif isinstance(payload, packet_pb2.SignedPacket):
            env.signed_packet.CopyFrom(payload)
        else:
            raise TypeError(f"Unsupported payload type: {type(payload)}")

        return env
