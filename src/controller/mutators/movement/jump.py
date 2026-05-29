from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("jump")
def jump(input: PlayerInput):
    input.jump = True
