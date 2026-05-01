from ui.components.component import UIComponent
from ui.components.container import UIContainer
from view import Renderable, Renderer

from typing import Any, Dict, List, Tuple

class UIPage:
    def __init__(self, id: str, meta: Dict[str, Any], elements: List[UIComponent]):
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
    
    def resolve_layout(self, screen_size: Tuple[int, int]):
        for root in self.elements:
            self.process_page_component(root, screen_size)
    
    def process_page_component(
        self,
        component: UIComponent,
        parent_size: Tuple[int, int],
        parent_pos: Tuple[int, int] = (0,0),
    ):
        pos = component.position

        x = pos["x"] * parent_size[0]
        y = pos["y"] * parent_size[1]

        abs_x = parent_pos[0] + x
        abs_y = parent_pos[1] + y

        component.absolute_position = (abs_x, abs_y)

        if "width" in component.size and "height" in component.size:
            component.absolute_size = (component.size["width"], component.size["height"])
        else:
            component.absolute_size = (0, 0)
        
        if hasattr(component, "children"):
            for child in getattr(component, "children"):
                self.process_page_component(
                    child,
                    component.absolute_size,
                    component.absolute_position
                )
    
    def submit_ui(self, renderer: Renderer):
        def submission_process_component(component: UIComponent, renderer: Renderer):
            component.process_component()

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
                    )
                )

                renderer.queue_renderable(renderable)

            if hasattr(component, "children"):
                for child in getattr(component, "children"):
                    submission_process_component(child, renderer)
        
        for root in self.elements:
            submission_process_component(root, renderer)