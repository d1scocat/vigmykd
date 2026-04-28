from context import GameContext
from pygame import Surface
from textures import TextureManager
from view.renderable import Renderable

from typing import Dict, List, Tuple


class Renderer:
    screen: Surface
    textures: TextureManager
    ctx: GameContext

    def __init__(self, screen: Surface, textures: TextureManager, ctx: GameContext):
        self.screen = screen
        self.textures = textures
        self.ctx = ctx
        self.render_queue: Dict[int, List[Tuple[Renderable, Surface]]] = {}

    def drop_queue(self):
        self.render_queue.clear()

    def queue_renderable(self, renderable: Renderable):
        surface = self._find_surface(renderable)
        if surface is None:
            return

        self.render_queue.setdefault(renderable.z_index, []).append(
            (renderable, surface)
        )

    def draw_renderable(self, renderable: Renderable):
        surface = self._find_surface(renderable)
        if surface is None:
            return

        self._draw_surface(renderable, surface)

    def draw_screen(self):
        self.screen.fill((0, 0, 0))

        for z in sorted(self.render_queue.keys()):
            # print(f"Drawing all renderables at {z=}")
            for renderable, surface in self.render_queue[z]:
                self._draw_surface(renderable, surface)
        self.drop_queue()

    def _find_surface(self, renderable: Renderable) -> Surface | None:
        state = renderable.states[renderable.current_state_id]
        sheet_id = state.sheet_id
        sheet_pos = state.grid_pos

        surface = self.textures.lookup_tile(sheet_id, sheet_pos)
        return surface

    def _draw_surface(self, renderable: Renderable, surface: Surface):
        state = renderable.states[renderable.current_state_id]
        loc_x, loc_y = renderable.location

        origin_x, origin_y = state.origin
        origin_x = surface.get_width() * origin_x
        origin_y = surface.get_height() * origin_y

        self.screen.blit(surface, (int(loc_x - origin_x), int(loc_y - origin_y)))
