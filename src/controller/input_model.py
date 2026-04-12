from dataclasses import dataclass


@dataclass
class PlayerInput:
    move_x: int = 0
    move_y: int = 0
    jump: bool = False
    dash: bool = False
    click_menu: bool = False
