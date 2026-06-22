from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("light")
def gravity_light(input: PlayerInput):
    input.gravity_light = True
