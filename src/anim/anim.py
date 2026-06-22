from dataclasses import dataclass
from typing import Final


@dataclass
class AnimationData:
    states: list[str]
    current_state: str
    idle_state: Final[str]
    idle_state_idx: Final[int]

    current_state_idx: int = 0

    @classmethod
    def from_renderable(
        cls,
        renderable: 'view.renderable.Renderable',
        idle_state: str,
        idle_state_idx: int
    ):
        states = list(renderable.states.keys())
        return cls(
            states=states,
            current_state=renderable.current_state,
            idle_state=idle_state,
            idle_state_idx=idle_state_idx,
        )

    def to_next(self):
        if self.current_state_idx == len(self.states) - 1:
            self.current_state_idx = 0
        else:
            self.current_state_idx += 1

        self.current_state = self.states[self.current_state_idx]

    def to_idle(self):
        self.current_state = self.states[self.idle_state_idx]
