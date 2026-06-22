from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("reverse_dash")
def reverse_dash(input: PlayerInput):
    input.reverse_dash = True
