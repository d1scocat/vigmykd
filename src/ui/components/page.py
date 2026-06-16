import settings

from context import GameContext
from ui.components.component import UIComponent
from ui.components.container import UIContainer
from ui.components.text import UITextHolder
from ui.components.textarea import UITextArea
from view import Renderable, Renderer

from typing import Any


class UIPage:
    def __init__(self, id: str, meta: dict[str, Any], elements: list[UIComponent]):
        self.id = id
        self.meta = meta
        self.elements = elements

    def find(self, target_id: str) -> UIComponent | None:
        stack = list(self.elements)

        while stack:
            el = stack.pop()
            if el.id == target_id:
                return el

            if isinstance(el, UIContainer):
                stack.extend(el.children)

        return None

    def process(self):
        for component in self.elements:
            component.process_component()

    def resolve_layout(self, screen_size: tuple[int, int], ctx: GameContext):
        for root in self.elements:
            self.process_page_component(root, ctx, screen_size)

    def process_page_component(
        self,
        component: UIComponent,
        ctx: GameContext,
        parent_size: tuple[int, int],
        parent_pos: tuple[int, int] = (0, 0),
    ):
        pos = component.position

        x = pos["x"] * parent_size[0]
        y = pos["y"] * parent_size[1]

        component.resolve_size(parent_size, ctx)

        w, h = component.absolute_size
        anchor_x, anchor_y = component.resolve_origin()

        abs_x = parent_pos[0] + x - w * anchor_x
        abs_y = parent_pos[1] + y - h * anchor_y

        component.absolute_position = (abs_x, abs_y)

        if isinstance(component, UIContainer):
            for child in component.children:
                self.process_page_component(
                    child,
                    ctx,
                    component.absolute_size,
                    component.absolute_position,
                )

    def submit_ui(self, renderer: Renderer):
        for root in self.elements:
            self._submission_process_component(root, renderer)

    def _submission_process_component(self, component: UIComponent, renderer: Renderer):
        if not component.resolved_visible:
            return

        states, current_state = component.build_render_states()

        if states:
            renderable = Renderable(
                z_index=component.z_index,
                states=states,
                current_state=current_state,
                location=(
                    int(component.absolute_position[0]),
                    int(component.absolute_position[1])
                ),
                size=component.absolute_size
            )

            renderer.queue_renderable(renderable)

        # Type checking happens inside the function itself as well,
        # so might as well skip it in here and just delegate it downwards
        self._submit_text(component, renderer)

        if isinstance(component, UIContainer):
            for child in component.children:
                self._submission_process_component(child, renderer)

    def _submit_text(self, component: UIComponent, renderer: Renderer):
        if not isinstance(component, UITextHolder) or component.text is None:
            return

        ctx = renderer.ctx
        base_text = component.text

        # For UITextElement
        content = getattr(component, "resolved_text_content", None)
        if not content:
            text_key = (base_text.raw or base_text.i18n)
            if not text_key:
                raise ValueError("base_text.raw and base_text.i18n cannot be None at"
                                 " the same time:", repr(base_text))
            content = \
                text_key \
                if base_text.raw \
                else ctx.localization.t(ctx.cfg.locale, text_key, False)

        if isinstance(component, UITextArea):
            if component.focused and not component.value:
                content = ""

        font_name = getattr(component, "resolved_font", base_text.font)
        font_size = getattr(component, "resolved_font_size", base_text.size)
        color = getattr(component, "resolved_color", base_text.color)

        font = ctx.fetch_font(font_name, font_size)
        surface = font.render(content, True, color)

        x, y = component.absolute_position
        w, h = component.absolute_size
        text_w, text_h = surface.get_size()

        if isinstance(component, UITextArea):
            draw_x = x + settings.PADDING_LEFT
            cursor = component.calculate_cursor(renderer)
            if cursor:
                renderer.queue_rect(component.z_index + 2, cursor, (0, 0, 0))
        else:
            draw_x = int(x + (w - text_w) / 2)

        draw_y = int(y + (h - text_h) / 2)

        renderer.queue_text(
            component.z_index + 1,
            surface,
            (draw_x, draw_y)
        )

    def by_id(self, id: str) -> UIComponent | None:
        stack = list(self.elements)
        while stack:
            el = stack.pop()
            if el.id == id:
                return el
            if isinstance(el, UIContainer):
                stack.extend(el.children)
        return None

    def by_type(self, type: str) -> list[UIComponent]:
        result = []
        stack = list(self.elements)
        while stack:
            el = stack.pop()
            if el.type == type:
                result.append(el)
            if isinstance(el, UIContainer):
                stack.extend(el.children)
        return result
