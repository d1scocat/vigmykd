import pygame

from game.model import GameState
from game.controller import Action
from typing import Callable, Dict, FrozenSet, Set, TypeAlias

Handler: TypeAlias = Callable[[float, GameState], None]


class InputHandler:
    action_names: Dict[str, Action]
    handlers: Dict[str, Handler]

    keymap: Dict[FrozenSet[int], str]

    activated: Set[FrozenSet[int]]

    def __init__(self):
        self.action_names = {}
        self.handlers = {}

        self.keymap = {}

        self.activated = set()

    def register_handler(self, name: str, continuous: bool, prio: int, func: Handler):
        action = Action(name, continuous, prio)

        self.action_names[name] = action
        self.handlers[name] = func

    def bind(self, combination: FrozenSet[int], action_name: str):
        self.keymap[combination] = action_name

        # for combo priority, sort them in descending order
        self.keymap = dict(
            sorted(
                self.keymap.items(),
                key=lambda x: (-self.action_names[x[1]].prio, -len(x[0])),
            )
        )

    def handle_input(self, dt: float, model: GameState):
        keys_state = pygame.key.get_pressed()
        used_keys: Set[int] = set()  # in use by higher-prio combos

        for keys, action_name in self.keymap.items():
            action = self.action_names.get(action_name)
            handler = self.handlers.get(action_name, None)
            if not action or not handler:
                continue  # todo log a warning

            active = all(keys_state[key] for key in keys)
            # skip if any key is in use by a higer-prio combo
            if active and keys & used_keys:
                continue

            # one-shot inputs
            if not action.continuous:
                if active and keys not in self.activated:
                    handler(dt, model)
                    self.activated.add(keys)
                    used_keys.update(keys)
                elif not active:
                    self.activated.discard(keys)
            # continuous inputs
            else:
                if active:
                    handler(dt, model)
                    used_keys.update(keys)
