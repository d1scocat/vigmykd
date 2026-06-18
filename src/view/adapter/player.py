import collections
import uuid

from game.model.state import GameState
from player.player import Player
from registry import register_adapter
from view.adapter.base import ViewAdapter
from view.renderable import Renderable, RenderState

from settings import PLAYER_WIDTH, SIMUL_DELAY_TICKS


@register_adapter(Player)
class PlayerAdapter(ViewAdapter[Player]):
    def __init__(self):
        self.position_hist: dict[uuid.UUID, collections.deque] = {}

    def create(self, object: Player) -> Renderable:
        self.position_hist[object.player_id] = collections.deque(maxlen=16)

        return Renderable(
            z_index=0,
            states={
                "0": RenderState(
                    sheet_id=1,
                    grid_pos=(0, 0),
                )
            },
            current_state="0",
            location=(object.position.x, object.position.y),
            size=(object.height, PLAYER_WIDTH)
        )

    def update(
        self,
        object: Player,
        renderable: Renderable,
        model: GameState,
        current_render_tick: float
    ):
        hist = self.position_hist.get(object.player_id)
        if hist is None:
            return

        if object.is_client:
            renderable.location = (object.position.x, object.position.y)
            return
        
        if not hist or model.last_server_tick > hist[-1][0]:
            hist.append((model.last_server_tick, object.position.x, object.position.y))

        if len(hist) < 2:
            renderable.location = (object.position.x, object.position.y)
            return

        delay = max(SIMUL_DELAY_TICKS, model.network_offset)
        target_tick = current_render_tick - delay

        state1 = state2 = None
        for i in range(len(hist) - 1):
            t1, x1, y1 = hist[i]
            t2, x2, y2 = hist[i+1]

            if t1 <= target_tick <= t2:
                state1 = (t1, x1, y1)
                state2 = (t2, x2, y2)
                break

        if not state1 or not state2:
            # not enough history
            renderable.location = (object.position.x, object.position.y)
            return

        # larp- no, lerp
        t1, x1, y1 = state1
        t2, x2, y2 = state2

        if t2 == t1:
            alpha = 0.0
        else:
            alpha = (target_tick - t1) / (t2 - t1)

        final_x = x1 + alpha * (x2 - x1)
        final_y = y1 + alpha * (y2 - y1)

        renderable.location = (final_x, final_y)