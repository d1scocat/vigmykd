import json
import pygame

from logging import Logger
from pathlib import Path
from typing import Dict, FrozenSet, List, Set

from registry import registries
from controller.input_model import Action, Mutation, BoundAction


class InputHandler:
    action_names: Dict[str, Action]
    keymap: Dict[FrozenSet[int], BoundAction]
    pressed_keys: Set[int]
    activated: Set[FrozenSet[int]]

    def __init__(self, assets_path: Path):
        with open(assets_path / "actions.json") as f:
            config = json.load(f)
            self.action_names = {
                name: Action(name, **data)
                for name, data in config.items()
            }

        self.keymap = {}
        self.pressed_keys = set()
        self.activated = set()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)

    def bind(self, combination: FrozenSet[int], action_name: str):
        action = self.action_names[action_name]
        mutator = registries.mutators[action_name]

        if mutator is None:
            raise ValueError(f"No mutator registered for action \"{action_name}\"")

        self.keymap[combination] = BoundAction(action, mutator)

        # for combo priority, sort them in descending order
        self.keymap = dict(
            sorted(
                self.keymap.items(),
                key=lambda x: (-x[1].action.prio, -len(x[0])),
            )
        )

    def handle_input(
        self,
        logger: Logger
    ) -> List[Mutation]:
        used_keys: Set[int] = set()  # in use by higher-prio combos
        result: List[Mutation] = []  # keep the order

        for keys, (action, mutator) in self.keymap.items():
            # action_name = action.name
            # mutator = registries.mutators[action_name]
            # if mutator is None:
            #     logger.warning(f"{action_name} has no input mutator")
            #     continue

            active = keys <= self.pressed_keys
            # skip if any key is in use by a higher-prio combo
            if active and keys & used_keys:
                continue

            # one-shot inputs
            if not action.continuous:
                if active and keys not in self.activated:
                    # handler(dt, model, ctx)
                    result.append(mutator)
                    self.activated.add(keys)
                    used_keys.update(keys)
                elif not active:
                    self.activated.discard(keys)

            # continuous inputs
            else:
                if active:
                    # handler(dt, model, ctx)
                    result.append(mutator)
                    used_keys.update(keys)

        return result
