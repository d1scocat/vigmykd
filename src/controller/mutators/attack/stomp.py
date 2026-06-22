from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("stomp")
def stomp(input: PlayerInput):
    input.stomp = True
