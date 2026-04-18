from view.adapter.base import ViewAdapter
from view.renderable import Renderable, RenderState
from registry import register_adapter
from player import Player


@register_adapter(Player)
class PlayerAdapter(ViewAdapter[Player]):
    def create(self, object: Player) -> Renderable:
        return Renderable(
            z_index=0,
            states={
                0: RenderState(
                    sheet_id=1,
                    grid_pos=(0, 0),
                    origin=(0.5, 0.5)
                )
            },
            current_state_id=0,
            # there will be an unnoticeable difference between the
            # real position and the rendered position (within 1 unit)
            location=(int(object.x), int(object.y))
        )
    
    def update(self, object: Player, renderable: Renderable):
        renderable.location = (int(object.x), int(object.y))