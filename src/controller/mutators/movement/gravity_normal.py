from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("normal")
def gravity_normal(input: PlayerInput):
    input.gravity_normal = True
