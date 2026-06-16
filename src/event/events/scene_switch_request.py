from dataclasses import dataclass

from event.model import Event


@dataclass
class SceneSwitchRequestEvent(Event):
    target: "scene.scene.Scene"

    def get_name(self) -> str:
        return "SceneSwitchRequestEvent"


@dataclass
class PrepareSceneRequestEvent(Event):
    scene: "scene.scene.Scene"

    def get_name(str) -> str:
        return "PrepareSceneRequestEvent"
