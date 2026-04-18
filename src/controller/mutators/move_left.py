from registry import register_mutator
from controller import PlayerInput


@register_mutator("move_left")
def move_left(input: PlayerInput):
    input.move_dx -= 1
