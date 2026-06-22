from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("parry")
def parry(input: PlayerInput):
    input.parry = True
