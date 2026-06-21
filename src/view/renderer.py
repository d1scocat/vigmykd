from context import GameContext
from textures import TextureManager
from view.renderable import Renderable

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

        self.render_queue: dict[int, list[tuple[Renderable, Surface]]] = {}
        self.static_render_queue: dict[int, list[tuple[Surface, tuple[float, float]]]] = {}
        self.text_queue: list[tuple[int, Surface, tuple[int, int], bool]] = []
        self.rect_queue: list[tuple[int, Rect, Color]] = []

        self.scale_cache: dict[tuple[int, tuple[int, int], int, int], Surface] = {}
        self.max_cache_size = ctx.cfg.max_scale_cache_size

    def drop_render_queue(self):
        self.render_queue.clear()

    def drop_static_queue(self):
        self.static_render_queue.clear()

    def drop_text_queue(self):
        self.text_queue.clear()

    def drop_rect_queue(self):
        self.rect_queue.clear()

    def clear_texture_scale_cache(self):
        self.scale_cache.clear()

    def drop_queue(self):
        self.drop_render_queue()
        self.drop_static_queue()
        self.drop_text_queue()
        self.drop_rect_queue()

    def queue_renderable(self, renderable: Renderable):
        surface = self._find_surface(renderable)
        if surface is None:
            return

        self.render_queue.setdefault(renderable.z_index, []).append((renderable, surface))

    def queue_static(self, surface: Surface, location: tuple[float, float], z_index: int = 0):
        self.static_render_queue.setdefault(z_index, []).append((surface, location))

    def queue_text(self, z_index: int, surface: Surface, pos: tuple[int, int], is_hud: bool = False):
        self.text_queue.append((z_index, surface, pos, is_hud))

    def queue_rect(
        self,
        z_index: int,
        dimensions: tuple[float, float, float, float],
        color: tuple[int, int, int]
    ):
        x, y, w, h = dimensions
        r, g, b = color
        self.rect_queue.append((
            z_index,
            Rect(x, y, w, h),
            Color(r, g, b)
        ))

    def draw_screen(self, camera_offset: tuple[float, float] = (0, 0)):
        self.screen.fill((0, 0, 0))

        for z in sorted(self.static_render_queue.keys()):
            for surface, location in self.static_render_queue[z]:
                self._draw_static(surface, location, camera_offset)

        for z in sorted(self.render_queue.keys()):
            for renderable, surface in self.render_queue[z]:
                self._draw_surface(renderable, surface, camera_offset)

        for z, surface, pos, is_hud in sorted(self.text_queue, key=lambda x: x[0]):
            pos = list(pos)
            if not is_hud:
                pos[0] += int(camera_offset[0])
                pos[1] += int(camera_offset[1])

            self.screen.blit(surface, pos)

        for z, rect, color in sorted(self.rect_queue, key=lambda x: x[0]):
            draw_rect = rect.copy()
            draw_rect.x += int(camera_offset[0])
            draw_rect.y += int(camera_offset[1])

            pygame.draw.rect(self.screen, color, draw_rect)

        self.drop_queue()

    def _find_surface(self, renderable: Renderable) -> Surface | None:
        state = renderable.states[renderable.current_state]
        sheet_id = state.sheet_id
        sheet_pos = state.grid_pos

        surface = self.textures.lookup_tile(sheet_id, sheet_pos)
        return surface

    def _draw_surface(self, renderable: Renderable, surface: Surface, offset: tuple[float, float]):
        loc_x, loc_y = renderable.location

        if not renderable.is_hud:
            loc_x += offset[0]
            loc_y += offset[1]

        w, h = renderable.size

        if renderable.flip_x or renderable.flip_y:
            surface = pygame.transform.flip(surface, renderable.flip_x, renderable.flip_y)

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

        final_surface = self.scale_cache[cache_key]
        if renderable.flip_x or renderable.flip_y:
            final_surface = pygame.transform.flip(final_surface,
                renderable.flip_x,
                renderable.flip_y
            )

        self.screen.blit(final_surface, loc)

    def _draw_static(self, surface: Surface, location: tuple[float, float], offset: tuple[float, float]):
        loc_x = location[0] + offset[0]
        loc_y = location[1] + offset[1]
        self.screen.blit(surface, (int(loc_x), int(loc_y)))
