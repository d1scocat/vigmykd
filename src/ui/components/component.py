from context import GameContext
from view import RenderState

from typing import Any


class UIComponent:
    # immutable
    states: dict[str, dict[str, Any]]
    default_state: str
    visible_by_default: bool
    is_hud: bool

    # produced by interaction system
    hovered: bool
    pressed: bool
    focused: bool

    # computed every frame
    resolved_state: str
    resolved_visible: bool
    resolved_texture: dict[str, Any] | None

    def __init__(
        self,
        id: str,
        type: str,
        z_index: int,
        position: dict[str, Any],
        size: dict[str, int],
        states: dict[str, dict[str, Any]] | None = None,
        default_state: str | None = None,
        is_hud: bool = False
    ):
        self.id = id
        self.type = type
        self.z_index = z_index
        self.is_hud = is_hud

        self.position = position
        self.size = size

        self.states = states or {}
        self.default_state = default_state or "normal"
        self.visible_by_default = True

        # runtime only flags
        self.hovered = False
        self.pressed = False
        self.focused = False

        # computed per frame
        self.resolved_visible = True
        self.resolved_texture = None

        self.base_state = default_state or "normal"

        self.absolute_position: tuple[int, int] = (0, 0)
        self.absolute_size: tuple[int, int] = (0, 0)

    def resolve_state(self) -> str:
        """
        Resolves the component state based on the current visual
        state (visible/hidden) and the logical state (hovered/pressed/normal).
        Interaction overrides logic.
        """
        if self.pressed:
            return "pressed"
        if self.hovered:
            return "hovered"
        return self.base_state

    def set_state(self, state: str):
        self.base_state = state

    def process_component(self):
        """
        Resolve the current visibility and texture in accordance
        to the current component state.
        """
        visible = self.resolved_visible
        texture = getattr(self, "texture", None)

        state = self.resolve_state()
        override = self.states.get(state, {})

        if "visible" in override:
            visible = override["visible"]

        if "texture" in override:
            texture = override["texture"]

        self.resolved_visible = visible
        self.resolved_texture = texture

        if hasattr(self, "children"):
            for child in getattr(self, "children"):
                child.process_component()

    def build_render_states(self) -> tuple[dict[str, RenderState], str]:
        base_texture = getattr(self, "texture", None)

        if not base_texture and not self.states:
            return {}, "normal"

        states: dict[str, RenderState] = {}
        all_state_names = set(self.states.keys()) | {"normal"}

        for state_name in all_state_names:
            override = self.states.get(state_name, {})
            texture = override.get("texture", base_texture)

            if texture is None:
                continue

            states[state_name] = RenderState(
                sheet_id=texture["sheet"],
                grid_pos=tuple(texture["tile"]),
                is_hud=self.is_hud
            )

        active_state = self.resolve_state()
        if active_state not in states:
            active_state = next(iter(states.keys()), "normal")

        return states, active_state

    def is_visible(self, parent_visible: bool = True) -> bool:
        state = self.resolve_state()
        override = self.states.get(state, {})
        local = override.get("visible", self.visible_by_default)

        return local and parent_visible

    def resolve_origin(self) -> tuple[float, float]:
        anchor = self.position.get("anchor", "top-left")

        return {
            "top-left": (0.0, 0.0),
            "center": (0.5, 0.5),
            "bottom-left": (0.0, 1.0),
            "top-right": (1.0, 0.0),
            "bottom-right": (1.0, 1.0),
        }.get(anchor, (0.0, 0.0))

    def resolve_size(
        self,
        parent_size: tuple[int, int],
        ctx: GameContext
    ):
        size = self.size
        if "width" in size and "height" in size:
            self.absolute_size = (size["width"], size["height"])
            return

        mode = size.get("mode")
        if mode == "match-texture":
            texture = self.resolved_texture
            if texture:
                surface = ctx.texture_manager.lookup_tile(texture["sheet"], tuple(texture["tile"]))
                if surface:
                    self.absolute_size = (surface.get_width(), surface.get_height())
                    return

        if mode == "fill":
            self.absolute_size = parent_size
            return

        if mode == "match-text" and hasattr(self, "resolved_text_key"):
            base_text = getattr(self, "text", None)
            if not base_text:
                raise ValueError(f"match-text mode requires UITextHolder on {self.id}")

            text_key = getattr(self, "resolved_text_key", base_text.raw or base_text.i18n)
            font_name = getattr(self, "resolved_font", base_text.font)
            font_size = getattr(self, "resolved_font_size", base_text.size)

            content = text_key if base_text.raw else ctx.ui_i18n(text_key, strict=False)
            font = ctx.fetch_font(font_name, font_size)

            self.absolute_size = font.size(content)
            self.resolved_text_content = content
            return

        raise ValueError(f"Unknown size for component {self.id=}, {self.type=}, {self.size=}")
