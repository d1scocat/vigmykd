from event.events import HTTPResponseEvent, SceneSwitchRequestEvent
from listeners import Listener
from scene.objects import MenuScene


class PubkeyListener(Listener[HTTPResponseEvent]):
    def __init__(self, ctx: "context.GameContext", model: "game.model.GameState"):
        super().__init__()
        self.ctx = ctx
        self.model = model

    def callback(self, event: HTTPResponseEvent):
        if event.endpoint != "/key/public":
            return
        if not event.success:
            return

        key = event.payload["key"]
        self.ctx.set_key(key)
        self.ctx.event_manager.invoke_event(SceneSwitchRequestEvent(
            target=MenuScene(self.model, self.ctx)
        ))
