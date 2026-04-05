from context import GameContext
from pygame import Surface
from textures import TextureManager
from view.renderable import Renderable


class Renderer:
    screen: Surface
    textures: TextureManager
    ctx: GameContext

    def __init__(self, screen: Surface, textures: TextureManager, ctx: GameContext):
        self.screen = screen
        self.textures = textures
        self.ctx = ctx

    def draw_renderable(self, renderable: Renderable):
        state = renderable.states[renderable.current_state_id]
        sheet_id = state.sheet_id
        sheet_pos = state.grid_pos

        surface = self.textures.lookup_tile(sheet_id, sheet_pos)
        if surface is None:
            return

        loc_x, loc_y = renderable.location

        origin_x, origin_y = state.origin
        origin_x = surface.get_width() * origin_x
        origin_y = surface.get_height() * origin_y

        self.screen.blit(surface, (int(loc_x - origin_x), int(loc_y - origin_y)))

    def draw_screen(self):
        pass
