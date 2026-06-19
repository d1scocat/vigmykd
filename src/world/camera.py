import pygame


class Camera:
    def __init__(self, screen_width: int, screen_height: int):
        self.x = 0.0
        self.y = 0.0
        self.width = screen_width
        self.height = screen_height

        self.smoothing = 0.1  # play around with this and later move to settings

    def follow(self, target: pygame.Rect):
        target_x = target.centerx - (self.width) / 2
        target_y = target.centery - (self.height) / 2

        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y -  self.y) * self.smoothing

    def clamp(self, map_width: int, map_height: int):
        if map_width <= self.width:
            self.x = (map_width - self.width) / 2
        else:
            self.x = max(0, min(self.x, map_width - self.width))

        if map_height <= self.height:
            self.y = (map_height - self.height) / 2
        else:
            self.y = max(0, min(self.y, map_height - self.height))

    @property
    def offset(self) -> tuple[float, float]:
        return (-self.x, -self.y)

    def world_to_screen_coordinate(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        return (world_pos[0] - self.x, world_pos[1] - self.y)

    def screen_to_world_coordinate(self, screen_pos: tuple[float, float]) -> tuple[float, float]:
        return (screen_pos[0] + self.x, screen_pos[1] + self.y)
