from game.model import GameState
from network.udp.factory import Packets


def request_match_info(model: GameState):
    packet = Packets.request_match_info()
    msg_id = packet.msg_id

    model.server_client.enqueue(Packets.envelope(packet), msg_id)
