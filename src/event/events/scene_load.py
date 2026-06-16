from dataclasses import dataclass

from event.model import Event


@dataclass
class ScenePreLoadEvent(Event):
    entered: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePreLoadEvent"


@dataclass
class ScenePostLoadEvent(Event):
    entered: "scene.scene.Scene"

    def get_name(self) -> str:
        return "ScenePostLoadEvent"
