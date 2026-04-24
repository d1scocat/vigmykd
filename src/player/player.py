import uuid

from geometry import BoundingBox2D
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_DUCK_HEIGHT


class Player:
    id: uuid.UUID

    def __init__(self, id: uuid.UUID):
        self.id = id
        self.x = 0.0
        self.y = 0.0

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.is_on_ground = True
        self.is_ducking = False

    @property
    def get_bounding_box(self) -> BoundingBox2D:
        return BoundingBox2D(
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )

    def toggle_duck_height(self, duck: bool):
        self.is_ducking = duck
        self.height = PLAYER_DUCK_HEIGHT if duck else PLAYER_HEIGHT

    @property
    def can_jump(self) -> bool:
        return self.is_on_ground
