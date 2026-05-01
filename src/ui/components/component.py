from view import Renderable, RenderState

from typing import Any, Dict, Tuple


class UIComponent:
    def __init__(
        self,
        id: str,
        type: str,
        z_index: int,
        position: Dict[str, Any],
        size: Dict[str, int],
        visible: bool = True,
        states: Dict[str, Dict[str, Any]] | None = None,
    ):
        self.id = id
        self.type = type
        self.z_index = z_index

        self.position = position
        self.size = size

        self.visible = visible
        self.states = states or {}

        self.visual_state: str | None = "normal"
        self.logical_state: str | None = "normal"

        self.resolved_visible: bool = visible
        self.resolved_texture: Dict[str, Any] | None = None

        self.absolute_position: Tuple[int, int] = (0, 0)
        self.absolute_size: Tuple[int, int] = (0, 0)

        self.hovered = False
    
    def resolve_state(self) -> str:
        # interaction overrides logic
        if self.visual_state:
            return self.visual_state
        if self.logical_state:
            return self.logical_state
        return "normal"
    
    def process_component(self):
        visible = self.visible
        texture = getattr(self, "texture", None)

        state = self.resolve_state()
        override = self.states.get(state, {})

        if "visible" in override:
            visible = override["visible"]

        if "texture" in override:
            texture = override["texture"]

        self.resolved_visible = visible
        self.resolved_texture = texture

    def build_render_states(self) -> Tuple[Dict[str, RenderState], str]:
        base_texture = getattr(self, "texture", None)

        if not base_texture and not self.states:
            return {}, "normal"
        
        states: Dict[str, RenderState] = {}

        all_state_names = set(self.states.keys())
        all_state_names.add("normal")  # ensure it exists bc it's the default state

        for state_name in all_state_names:
            override = self.states.get(state_name, {})
            texture = override.get("texture", base_texture)

            if texture is None:
                continue

            states[state_name] = RenderState(
                sheet_id=texture["sheet"],
                grid_pos=tuple(texture["tile"]),
                origin=self._resolve_origin()
            )
        
        active_state = self.resolve_state()
        if active_state not in states:
            active_state = next(iter(states.keys()), "normal")
        
        return states, active_state

    def _resolve_origin(self) -> Tuple[float, float]:
        anchor = self.position.get("anchor", "top-left")

        return {
            "top-left": (0.0, 0.0),
            "center": (0.5, 0.5),
            "bottom-left": (0.0, 1.0),
            "top-right": (1.0, 0.0),
            "bottom-right": (1.0, 1.0),
        }.get(anchor, (0.0, 0.0))