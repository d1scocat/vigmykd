from dataclasses import dataclass


@dataclass
class PlayerInput:
    move_dx: int = 0
    move_dy: int = 0
    jump: bool = False
    dash: bool = False
    click_menu: bool = False
