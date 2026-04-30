from event.model import Event


class ScenePreEnterEvent(Event):
    from scene.scene import Scene  # type-checking purposes

    entered: Scene

    def __init__(self, scene: Scene) -> None:
        self.entered = scene

    def get_name(self) -> str:
        return "ScenePreEnterEvent"


class ScenePostEnterEvent(Event):
    from scene.scene import Scene  # type-checking purposes

    entered: Scene

    def __init__(self, scene: Scene) -> None:
        self.entered = scene

    def get_name(self) -> str:
        return "ScenePostEnterEvent"