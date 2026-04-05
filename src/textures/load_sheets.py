from textures import load_spritesheet, TextureManager
from context import GameContext


def load_sheets(ctx: GameContext, manager: TextureManager):
    manager.add_spritesheet(
        id=1,
        sheet=load_spritesheet(
            path=ctx.assets_path / "player-spreadsheet.png",
            tile_size=(44, 44),
            grid_size=(9, 41)
        )
    )
