from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("dash")
def dash(input: PlayerInput):
    input.dash = True
