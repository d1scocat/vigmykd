from context import GameContext
from event.events import HTTPResponseEvent
from listeners import Listener

class LoginListener(Listener[HTTPResponseEvent]):
    def __init__(self, ctx: GameContext):
        super().__init__()
        self.ctx = ctx

    def callback(self, event: HTTPResponseEvent):
        if event.endpoint != "/auth/login":
            return
        if not event.success:
            return

        result = event.payload["token"]
        self.ctx.auth.set_token(result)
