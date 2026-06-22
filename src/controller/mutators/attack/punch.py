from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("punch")
def punch(input: PlayerInput):
    input.punch = True
