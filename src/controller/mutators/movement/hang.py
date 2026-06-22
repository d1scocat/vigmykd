from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("hang")
def hang(input: PlayerInput):
    input.hang = True
