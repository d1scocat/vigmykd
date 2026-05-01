from typing import List, Tuple

from ui.components.component import UIComponent
from ui.components.container import UIContainer

class UIInteractionSystem:
    def __init__(self):
        self.active_component: UIComponent | None = None
        self.prev_mouse_down: bool = False

    def update(
        self,
        components: List[UIComponent],
        mouse_pos: Tuple[int, int],
        mouse_down: bool
    ) -> str | None:
        flattened = self._flatten_dfs(components)
        flattened.sort(key=lambda c: c.z_index, reverse=True)

        handled = False

        for component in flattened:
            if handled:
                component.visual_state = "normal"
                component.hovered = False
                continue

            handled = self._process_single(component, mouse_pos, mouse_down)

        action = None
        if self.prev_mouse_down and not mouse_down:
            action = self._handle_release(mouse_pos)

        self.prev_mouse_down = mouse_down
        return action

    def _flatten_dfs(self, components: List[UIComponent]) -> List[UIComponent]:
        result = []

        def dfs(comp: UIComponent, parent_visible: bool):
            state = comp.resolve_state()
            override = comp.states.get(state, {})
            visible = override.get("visible", comp.visible) or parent_visible

            if not visible:
                return
            
            result.append(comp)
            if isinstance(comp, UIContainer):
                for child in comp.children:
                    dfs(child, visible)

        for component in components:
            dfs(component, True)

        return result

    def _process_single(
        self,
        component: UIComponent,
        mouse_pos: Tuple[int, int],
        mouse_down: bool,
        parent_visible: bool = True
    ) -> bool:
        state = component.resolve_state()
        override = component.states.get(state, {})
        visible = override.get("visible", component.visible) and parent_visible
        if not visible:
            return False

        if not hasattr(component, "absolute_position"):
            return False

        x, y = component.absolute_position
        w, h = getattr(component, "absolute_size", (0, 0))
        m_x, m_y = mouse_pos

        inside = x <= m_x <= x + w and y <= m_y <= y + h
        if inside:
            component.hovered = True
            if mouse_down:
                component.visual_state = "pressed"
                if not self.prev_mouse_down and hasattr(component, "action"):
                    self.active_component = component
            else:
                component.visual_state = "hover"
            return True

        component.hovered = False
        component.visual_state = "normal"
        return False


    def _handle_release(self, mouse_pos: Tuple[int, int]) -> str | None:
        if not self.active_component:
            return

        comp = self.active_component
        x, y = comp.absolute_position
        w, h = getattr(comp, "absolute_size", (0, 0))
        m_x, m_y = mouse_pos

        action = None
        inside = x <= m_x <= x + w and y <= m_y <= y + h
        if inside:
            action = self._trigger_action(comp)

        self.active_component = None
        return action

    def _trigger_action(self, component: UIComponent) -> str | None:
        action: str | None = getattr(component, "action", None)
        return action
