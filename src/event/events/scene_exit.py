from dataclasses import dataclass

from event.model import Event


@dataclass
class ScenePreExitEvent(Event):
    exited: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePreExitEvent"


@dataclass
class ScenePostExitEvent(Event):
    exited: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePostExitEvent"
