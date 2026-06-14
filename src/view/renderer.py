from context import GameContext
from textures import TextureManager
from view.renderable import Renderable

from typing import Dict, List, Tuple

from pygame import Surface, Rect, Color
import pygame


class Renderer:
    screen: Surface
    textures: TextureManager
    ctx: GameContext

    def __init__(self, screen: Surface, textures: TextureManager, ctx: GameContext):
        self.screen = screen
        self.textures = textures
        self.ctx = ctx

        self.render_queue: Dict[int, List[Tuple[Renderable, Surface]]] = {}
        self.text_queue: List[Tuple[int, Surface, Tuple[int, int]]] = []
        self.rect_queue: List[Tuple[int, Rect, Color]] = []

        self.scale_cache: Dict[Tuple[int, Tuple[int, int], int, int], Surface] = {}
        self.max_cache_size = 2**14 - 1  # Later extract into settings

    def drop_render_queue(self):
        self.render_queue.clear()

    def drop_text_queue(self):
        self.text_queue.clear()

    def drop_rect_queue(self):
        self.rect_queue.clear()

    def clear_texture_scale_cache(self):
        self.scale_cache.clear()

    def drop_queue(self):
        self.drop_render_queue()
        self.drop_text_queue()
        self.drop_rect_queue()

    def queue_renderable(self, renderable: Renderable):
        surface = self._find_surface(renderable)
        if surface is None:
            return

        self.render_queue.setdefault(renderable.z_index, []).append(
            (renderable, surface)
        )

    def queue_text(self, z_index: int, surface: Surface, pos: Tuple[int, int]):
        self.text_queue.append((z_index, surface, pos))

    def queue_rect(
        self,
        z_index: int,
        dimensions: Tuple[float, float, float, float],
        color: Tuple[int, int, int]
    ):
        x, y, w, h = dimensions
        r, g, b = color
        self.rect_queue.append((
            z_index,
            Rect(x, y, w, h),
            Color(r, g, b)
        ))

    def draw_renderable(self, renderable: Renderable):
        surface = self._find_surface(renderable)
        if surface is None:
            return

        self._draw_surface(renderable, surface)

    def draw_screen(self):
        self.screen.fill((0, 0, 0))

        for z in sorted(self.render_queue.keys()):
            for renderable, surface in self.render_queue[z]:
                self._draw_surface(renderable, surface)

        for z, surface, pos in sorted(self.text_queue, key=lambda x: x[0]):
            self.screen.blit(surface, pos)

        for z, rect, color in sorted(self.rect_queue, key=lambda x: x[0]):
            pygame.draw.rect(self.screen, color, rect)

        self.drop_queue()

    def _find_surface(self, renderable: Renderable) -> Surface | None:
        state = renderable.states[renderable.current_state]
        sheet_id = state.sheet_id
        sheet_pos = state.grid_pos

        surface = self.textures.lookup_tile(sheet_id, sheet_pos)
        return surface

    def _draw_surface(self, renderable: Renderable, surface: Surface):
        loc_x, loc_y = renderable.location
        w, h = renderable.size

        if surface.get_size() == (w, h):
            self.screen.blit(surface, (int(loc_x), int(loc_y)))
            return

        loc = (int(loc_x), int(loc_y))

        state = renderable.states[renderable.current_state]
        cache_key = (state.sheet_id, state.grid_pos, w, h)

        if cache_key not in self.scale_cache:
            if len(self.scale_cache) >= self.max_cache_size:
                self.screen.blit(pygame.transform.smoothscale(surface, (w, h)), loc)
                return

            self.scale_cache[cache_key] = pygame.transform.smoothscale(surface, (w, h))
        self.screen.blit(self.scale_cache[cache_key], loc)
