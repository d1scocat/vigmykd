import pygame

from textures import loader, TextureManager
from world import Camera, HeadlessWorld


class World:
    render_surface: pygame.Surface

    def __init__(
        self,
        headless: HeadlessWorld,
        texture_manager: TextureManager,
        sheet_id: int
    ):
        self.texture_manager = texture_manager
        self.sheet_id = sheet_id
        self.headless = headless

        self.map_width = headless.map_data.width * headless.map_data.tile_width
        self.map_height = headless.map_data.height * headless.map_data.tile_height

        self.render_surface = self._build_render_surface()

        display_info = pygame.display.Info()

        screen_width = display_info.current_w
        screen_height = display_info.current_h

        self.camera = Camera(screen_width, screen_height)

    def _build_render_surface(self):
        surface = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)

        tw, th = self.headless.map_data.tile_width, self.headless.map_data.tile_height
        w, h = self.headless.map_data.width, self.headless.map_data.height

        for y in range(h):
            for x in range(w):
                gid = self.headless.map_data.grid[y][x]
                if gid == 0:
                    continue

                sprite_x, sprite_y = self.headless.tileset.get_sprite_coords(gid)
                sprite = self.texture_manager.lookup_tile(self.sheet_id, (sprite_x, sprite_y))

                if sprite:
                    surface.blit(sprite, (x * tw, y * th))

        return surface

    def prep_render(self, player: pygame.Rect):
        self.camera.follow(player)
        self.camera.clamp(self.map_width, self.map_height)
