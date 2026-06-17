from dataclasses import dataclass
from typing import Callable, NamedTuple


@dataclass
class PlayerInput:
    # Movement
    move_dir: int = 0
    duck: bool = False
    jump: bool = False
    dash: bool = False


@dataclass
class Action:
    name: str
    continuous: bool
    prio: int


Mutation = Callable[[PlayerInput], None]  # in-place editor


class BoundAction(NamedTuple):  # type hints
    action: Action
    mutator: Mutation
