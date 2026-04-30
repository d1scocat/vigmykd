from event.model import Event


class ScenePreExitEvent(Event):
    from scene.scene import Scene  # type-checking purposes

    exited: Scene

    def __init__(self, scene: Scene) -> None:
        self.exited = scene

    def get_name(self) -> str:
        return "ScenePreExitEvent"


class ScenePostExitEvent(Event):
    from scene.scene import Scene  # type-checking purposes

    exited: Scene

    def __init__(self, scene: Scene) -> None:
        self.exited = scene

    def get_name(self) -> str:
        return "ScenePostExitEvent"
