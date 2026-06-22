from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("push")
def push(input: PlayerInput):
    input.push = True
