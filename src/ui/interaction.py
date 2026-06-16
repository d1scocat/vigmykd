from ui.components.component import UIComponent
from ui.components.container import UIContainer
from ui.components.textarea import UITextArea

import pygame


class UIInteractionSystem:
    def __init__(self):
        self.active_component: UIComponent | None = None
        self.focused_component: UIComponent | None = None
        self.prev_mouse_down: bool = False

    def update(
        self,
        components: list[UIComponent],
        mouse_pos: tuple[int, int],
        mouse_down: bool
    ) -> str | None:
        flattened = self._flatten_dfs(components)
        flattened.sort(key=lambda c: c.z_index, reverse=True)

        for component in flattened:
            component.pressed = False
            component.hovered = False

        handled = False

        for component in flattened:
            if handled:
                component.pressed = False
                component.hovered = False
                continue

            handled = self._process_single(component, mouse_pos, mouse_down)

        action = None
        if self.prev_mouse_down and not mouse_down:
            action = self._handle_release(mouse_pos)

        self.prev_mouse_down = mouse_down
        return action

    def handle_key(self, event: pygame.event.Event, components: list[UIComponent]):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_TAB:
            focusables = self._get_focusable(components)
            if not focusables:
                return

            if self.focused_component not in focusables:
                next_comp = focusables[0]
            else:
                idx = focusables.index(self.focused_component)

                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    idx -= 1
                else:
                    idx += 1

                next_comp = focusables[idx % len(focusables)]

            # should always be true
            # but when ill be adding more focusable components,
            # i'll abstract this into UIFocusable
            if isinstance(next_comp, UITextArea):
                self._set_focus(next_comp)

    def _set_focus(self, component: UITextArea):
        if self.focused_component:
            self.focused_component.focused = False

        self.focused_component = component
        component.focused = True

        if hasattr(component, "value"):
            component.cursor = len(component.value)

    def _flatten_dfs(self, components: list[UIComponent]) -> list[UIComponent]:
        result = []

        def dfs(comp: UIComponent, parent_visible: bool):
            visible = comp.is_visible(parent_visible)
            if not visible:
                return

            result.append(comp)
            if isinstance(comp, UIContainer):
                for child in comp.children:
                    dfs(child, visible)

        for component in components:
            dfs(component, True)

        return result

    def _get_focusable(self, components: list[UIComponent]) -> list[UIComponent]:
        flat = self._flatten_dfs(components)
        return [comp for comp in flat if isinstance(comp, UITextArea)]

    def _process_single(
        self,
        component: UIComponent,
        mouse_pos: tuple[int, int],
        mouse_down: bool,
        parent_visible: bool = True
    ) -> bool:
        if not component.is_visible(parent_visible):
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
                component.pressed = True
                if not self.prev_mouse_down and hasattr(component, "action"):
                    self.active_component = component

                if isinstance(component, UITextArea):
                    self._set_focus(component)
            return True
        else:
            component.hovered = False
            component.pressed = False

            if mouse_down and self.focused_component:
                self.focused_component.focused = False
                self.focused_component = None

        return False

    def _handle_release(self, mouse_pos: tuple[int, int]) -> str | None:
        if not self.active_component:
            return None

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
