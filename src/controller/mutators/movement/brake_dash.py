from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("brake_dash")
def brake_dash(input: PlayerInput):
    input.brake_dash = True
