from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("duck")
def duck(input: PlayerInput):
    input.duck = True
