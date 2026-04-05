from pygame import Surface


class Renderer:
    screen: Surface

    def __init__(self, screen: Surface):
        self.screen = screen

    def draw_screen(self):
        pass
