import pygame
from context import GameContext
from controller import Action, PlayerInput
from typing import Callable, Dict, FrozenSet, Set, TypeAlias

Mutation: TypeAlias = Callable[[PlayerInput], PlayerInput]


class InputHandler:
    action_names: Dict[str, Action]
    mutators: Dict[str, Mutation]
    keymap: Dict[FrozenSet[int], str]
    pressed_keys: Set[int]
    activated: Set[FrozenSet[int]]

    def __init__(self):
        self.action_names = {}
        self.mutators = {}
        self.keymap = {}
        self.pressed_keys = set()
        self.activated = set()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)

    def register_mutator(self, name: str, func: Mutation):
        self.mutators[name] = func

    def bind(self, combination: FrozenSet[int], action_name: str):
        self.keymap[combination] = action_name

        # for combo priority, sort them in descending order
        self.keymap = dict(
            sorted(
                self.keymap.items(),
                key=lambda x: (-self.action_names[x[1]].prio, -len(x[0])),
            )
        )

    def handle_input(self, ctx: GameContext) -> Set[Mutation]:
        used_keys: Set[int] = set()  # in use by higher-prio combos
        result: Set[Mutation] = set()

        for keys, action_name in self.keymap.items():
            action = self.action_names.get(action_name)
            if not action:
                ctx.logger.warning(f"{action_name} is not a valid action")
                continue

            mutator = self.mutators.get(action_name)
            if not mutator:
                ctx.logger.warning(f"{action_name} has no input mutator")
                continue

            active = keys <= self.pressed_keys
            # skip if any key is in use by a higher-prio combo
            if active and keys & used_keys:
                continue

            # one-shot inputs
            if not action.continuous:
                if active and keys not in self.activated:
                    # handler(dt, model, ctx)
                    result.add(mutator)
                    self.activated.add(keys)
                    used_keys.update(keys)
                elif not active:
                    self.activated.discard(keys)
            # continuous inputs
            else:
                if active:
                    # handler(dt, model, ctx)
                    result.add(mutator)
                    used_keys.update(keys)

        return result
