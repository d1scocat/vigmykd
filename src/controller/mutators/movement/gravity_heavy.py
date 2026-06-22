from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("heavy")
def gravity_heavy(input: PlayerInput):
    input.gravity_heavy = True
