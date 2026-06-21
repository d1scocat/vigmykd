import json

from dataclasses import dataclass, field
from pathlib import Path

from geometry import Rect


@dataclass
class Tileset:
    cols: int
    tile_width: int
    tile_height: int
    first_gid: int
    collisions: dict[int, list[Rect]] = field(default_factory=dict)

    @classmethod
    def load(cls, tsj_path: Path, first_gid: int) -> 'Tileset':
        data = json.loads(tsj_path.read_text())

        cols = data["columns"]
        tile_width = data["tilewidth"]
        tile_height = data["tileheight"]

        collisions = {}

        for tile_data in data.get("tiles", []):
            tile_id = tile_data["id"]  # zero-indexed

            if "objectgroup" in tile_data:
                tile_collisions = []
                for obj in tile_data["objectgroup"]["objects"]:
                    tile_collisions.append(Rect(
                        obj["x"], obj["y"], obj["width"], obj["height"]
                    ))

                collisions[tile_id] = tile_collisions

        return cls(
            cols=cols,
            tile_width=tile_width,
            tile_height=tile_height,
            first_gid=first_gid,
            collisions=collisions
        )

    def get_sprite_coords(self, map_gid: int) -> tuple[int, int]:
        tile_id = map_gid - self.first_gid

        x = tile_id % self.cols
        y = tile_id // self.cols
        return (x, y)


class Layer:
    pass


@dataclass
class TileLayer(Layer):
    grid: list[list[int]]


@dataclass
class ImageLayer(Layer):
    name: str
    path: Path
    width: int
    height: int
    x: float
    y: float
    opacity: float
    repeat_x: bool 
    repeat_y: bool


@dataclass
class MapData:
    width: int
    height: int
    tile_width: int
    tile_height: int
    first_gid: int
    layers: list[Layer]

    @property
    def grid(self) -> list[list[int]]:
        for layer in self.layers:
            if isinstance(layer, TileLayer):
                return layer.grid
        raise ValueError("No tile layer to get the grid from")

    @classmethod
    def load(cls, tmj_path: Path) -> 'MapData':
        data = json.loads(tmj_path.read_text())
        base_dir = tmj_path.parent

        width= data["width"]
        height = data["height"]
        tile_width = data["tilewidth"]
        tile_height = data["tileheight"]
        first_gid = data["tilesets"][0]["firstgid"]

        layers = []

        for layer in data["layers"]:
            if not layer.get("visible", True):
                continue

            if layer["type"] == "tilelayer":
                fl_data = layer["data"]
                grid = []

                for y in range(height):
                    grid.append(fl_data[(y * width):((y+1)*width)])
                layers.append(TileLayer(grid))

            elif layer["type"] == "imagelayer":
                img_path = base_dir / layer["image"]
                layers.append(ImageLayer(
                    name=layer.get("name", ""),
                    path=img_path,
                    width=layer["imagewidth"],
                    height=layer["imageheight"],
                    x=float(layer.get("x", 0.0)),
                    y=float(layer.get("y", 0.0)),
                    opacity=float(layer.get("opacity", 1.0)),
                    repeat_x=layer.get("repeatx", False),
                    repeat_y=layer.get("repeaty", False),
                ))

        if not any(isinstance(layer, TileLayer) for layer in layers):
            raise ValueError(f"No visible TileLayer in tmj {tmj_path.resolve()}")

        return cls(
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
            first_gid=first_gid,
            layers=layers
        )


class HeadlessWorld:
    collision_grid: list[list[list[Rect]]]

    def __init__(
        self,
        tmj_path: Path,
        tsj_path: Path,
        first_spawn: tuple[float, float],
        second_spawn: tuple[float, float]
    ):
        self.map_data = MapData.load(tmj_path)
        self.tileset = Tileset.load(tsj_path, self.map_data.first_gid)
        self.spawns = {1: first_spawn, 2: second_spawn}

        self._build_collision_grid()

    def get_collision(self, rect: Rect) -> Rect | None:
        tw, th = self.map_data.tile_width, self.map_data.tile_height
        w, h = self.map_data.width, self.map_data.height

        start_x = int(max(0, rect.left // tw))
        end_x= int(min(w - 1, rect.right // tw))
        
        start_y = int(max(0, rect.top // th))
        end_y = int(min(h - 1, rect.bottom // th))

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                for coll in self.collision_grid[y][x]:
                    if rect.colliderect(coll):
                        return coll
        return None

    def _build_collision_grid(self):
        self.collision_grid = [
            [[] for _ in range(self.map_data.width)]
            for _ in range(self.map_data.height)
        ]

        tw, th = self.map_data.tile_width, self.map_data.tile_height
        w, h = self.map_data.width, self.map_data.height

        for y in range(h):
            for x in range(w):
                gid = self.map_data.grid[y][x]
                if gid == 0:
                    continue  # empty space

                tile_id = gid - self.tileset.first_gid
                local_collisions = self.tileset.collisions.get(tile_id, [])

                for coll in local_collisions:
                    self.collision_grid[y][x].append(Rect(
                        x * tw + coll.x,
                        y * th + coll.y,
                        coll.width,
                        coll.height
                    ))