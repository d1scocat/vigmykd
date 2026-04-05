from dataclasses import dataclass


@dataclass
class Action:
    name: str
    continuous: bool
    prio: int
