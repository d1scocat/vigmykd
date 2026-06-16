from context import GameContext
from event.events import SceneSwitchRequestEvent
from game.model import GameState
from network.udp.factory import Packets
from scene.scene import Scene
from scene.objects.menu import MenuScene


def quit_matchmaking(scene: Scene, model: GameState, ctx: GameContext):
    packet = Packets.matchmaking_quit()
    msg_id = packet.msg_id

    model.server_client.enqueue(Packets.envelope(packet), msg_id)

    ctx.event_manager.invoke_event(SceneSwitchRequestEvent(MenuScene(model, ctx)))
