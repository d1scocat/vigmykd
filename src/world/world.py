import pygame

from textures import TextureManager
from world import Camera, HeadlessWorld, TileLayer, ImageLayer


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

        for layer in self.headless.map_data.layers:
            if isinstance(layer, TileLayer):
                surface = self._add_tilelayer_to_surface(tw, th, w, h, layer, surface)
            elif isinstance(layer, ImageLayer):
                surface = self._add_imagelayer_to_surface(layer, surface)

        return surface

    def _add_tilelayer_to_surface(
        self,
        tw: int, th: int, w: int, h: int,
        layer: TileLayer,
        surface: pygame.Surface
    ) -> pygame.Surface:
        for y in range(h):
            for x in range(w):
                gid = layer.grid[y][x]
                if gid == 0:
                    continue

                sprite_x, sprite_y = self.headless.tileset.get_sprite_coords(gid)
                sprite = self.texture_manager.lookup_tile(self.sheet_id, (sprite_x, sprite_y))

                if sprite:
                    pos_x = x * tw
                    pos_y = y * th
                    surface.blit(sprite, (pos_x, pos_y))

        return surface

    def _add_imagelayer_to_surface(self, layer: ImageLayer, surface: pygame.Surface) -> pygame.Surface:
        try:
            img_surface = pygame.image.load(str(layer.path)).convert_alpha()
        except pygame.error as ex:
            raise ValueError(f"Could not load image layer from {layer.path.resolve()}") from ex
        
        img_surface.set_alpha(int(255 * layer.opacity))

        img_w, img_h = layer.width, layer.height
        start_x, start_y = layer.x, layer.y

        if layer.repeat_x or layer.repeat_y:
            end_x = self.map_width if layer.repeat_x else start_x + img_w
            end_y =  self.map_height if layer.repeat_y else start_y + img_h

            cur_y = start_y
            while cur_y < end_y:
                cur_x = start_x
                while cur_x < end_x:
                    surface.blit(img_surface, (int(cur_x), int(cur_y)))
                    cur_x += img_w
                cur_y += img_h
        else:
            surface.blit(img_surface, (int(start_x), int(start_y)))

        return surface

    def prep_render(self, player: pygame.Rect):
        self.camera.follow(player)
        self.camera.clamp(self.map_width, self.map_height)
