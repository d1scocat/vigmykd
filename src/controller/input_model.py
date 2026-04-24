from dataclasses import dataclass
from typing import Callable, NamedTuple, TypeAlias


@dataclass
class PlayerInput:
    # Movement
    move_dx: int = 0
    duck: bool = False
    jump: bool = False
    dash: bool = False

    # Navigation
    menu_next: bool = False
    menu_prev: bool = False
    menu_ok: bool = False


@dataclass
class Action:
    name: str
    continuous: bool
    prio: int


Mutation: TypeAlias = Callable[[PlayerInput], None]  # in-place editor


class BoundAction(NamedTuple):  # type hints
    action: Action
    mutator: Mutation
