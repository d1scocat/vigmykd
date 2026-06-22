import collections
import uuid

from anim import AnimationData
from game.model.state import GameState
from player.player import Facing, Player
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

        result = Renderable(
            z_index=1000,
            states={
                "0": RenderState(sheet_id=1, grid_pos=(0, 0), is_hud=False),
                "1": RenderState(sheet_id=1, grid_pos=(3, 0), is_hud=False),
                "2": RenderState(sheet_id=1, grid_pos=(4, 0), is_hud=False),
                "3": RenderState(sheet_id=1, grid_pos=(5, 0), is_hud=False),
                "4": RenderState(sheet_id=1, grid_pos=(6, 0), is_hud=False),
                "5": RenderState(sheet_id=1, grid_pos=(7, 0), is_hud=False),
                "6": RenderState(sheet_id=1, grid_pos=(8, 0), is_hud=False),
            },
            current_state="0",
            location=(object.position.x, object.position.y),
            size=(object.height, PLAYER_WIDTH)
        )

        object.anim = AnimationData.from_renderable(result, "0", 0)

        return result

    def update(
        self,
        object: Player,
        renderable: Renderable,
        model: GameState,
        current_render_tick: float
    ):
        def apply_current(x: float, y: float):
            renderable.location = (x, y)
            renderable.flip_x = (object.position.facing == Facing.NEG_X)
            renderable.current_state = str(object.anim.current_state)

        hist = self.position_hist.get(object.player_id)
        if hist is None:
            return

        if object.is_client:
            apply_current(object.position.x, object.position.y)
            return
        
        if not hist or model.last_server_tick > hist[-1][0]:
            hist.append((model.last_server_tick, object.position.x, object.position.y))

        if len(hist) < 2:
            apply_current(object.position.x, object.position.y)
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
            apply_current(object.position.x, object.position.y)
            return

        # larp- no, lerp
        t1, x1, y1 = state1
        t2, x2, y2 = state2

        alpha = 0.0 if t1 == t2 else (target_tick - t1) / (t2 - t1)

        final_x = x1 + alpha * (x2 - x1)
        final_y = y1 + alpha * (y2 - y1)

        apply_current(final_x, final_y)
