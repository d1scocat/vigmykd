from dataclasses import dataclass

from event.model import Event


@dataclass
class ScenePreEnterEvent(Event):
    entered: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePreEnterEvent"


@dataclass
class ScenePostEnterEvent(Event):
    entered: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePostEnterEvent"
