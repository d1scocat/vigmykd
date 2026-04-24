from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("move_right")
def move_left(input: PlayerInput):
    input.move_dx += 1
