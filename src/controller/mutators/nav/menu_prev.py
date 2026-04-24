from registry import register_mutator
from controller.input_model import PlayerInput


@register_mutator("menu_prev")
def menu_next(input: PlayerInput):
    input.menu_prev = True
