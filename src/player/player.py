import uuid


from geometry import BoundingBox2D


class Player:
    id: uuid.UUID

    def __init__(self, id: uuid.UUID):
        self.player_id = id
        self.x = 0.0
        self.y = 0.0

        self.velocity_x = 0.0
        self.velocity_y = 0.0
    
    @property
    def get_bounding_box(self) -> BoundingBox2D:
        ...