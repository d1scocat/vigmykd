from controller import InputHandler
from controller.handlers import handler_move_left, handler_move_right, handler_move_up
from controller.handlers import \
    handler_move_duck


def register_all(input_handler: InputHandler):
    input_handler.register_handler("move_up", True, 0, handler_move_up.handle)
    input_handler.register_handler("move_left", True, 0, handler_move_left.handle)
    input_handler.register_handler("move_right", True, 0, handler_move_right.handle)
    input_handler.register_handler("move_duck", True, 0, handler_move_duck.handle)
