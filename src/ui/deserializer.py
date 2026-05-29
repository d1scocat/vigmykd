from typing import Any, Dict

from ui.components import button, component, container, image, page, \
    text, textarea


def build_component(obj: Dict[str, Any]) -> component.UIComponent:
    type = obj["type"].lower()

    id = obj["id"]
    z_index = obj.get("z_index", 0)
    position = obj["position"]
    size = obj["size"]
    texture = obj.get("texture", None)

    states = obj.get("states", {})

    default_state = obj.get("default-state")
    if default_state is None:
        default_state = next(iter(states.keys()), "normal")

    comp: component.UIComponent | None = None

    match type:
        case "button" | "btn":
            comp = button.UIButton(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                states=states,
                action=obj["action"],
                text=obj.get("text"),
                default_state=default_state
            )

        case "image":
            comp = image.UIImage(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture,
                default_state=default_state
            )

        case "form" | "container":
            children = [build_component(child) for child in obj.get("children", [])]
            comp = container.UIContainer(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture,
                children=children,
                states=states,
                default_state=default_state
            )

        case "textarea":
            comp = textarea.UITextArea(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture,
                label=obj["label"],
                hint=obj["hint"],
                states=states,
                default_state=default_state
            )

        case "text":
            comp = text.UITextElement(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                text=obj.get("text", {}),
                states=states,
                default_state=default_state
            )

        case _:
            raise ValueError(f"Undefined component type '{type}' with id '{id}'")

    comp.visible_by_default = obj.get("visible", True)

    return comp


def deserialize_into_ui(data: Dict[str, Any]) -> page.UIPage:
    elements = [build_component(elem) for elem in data["elements"]]
    return page.UIPage(
        id=data["id"],
        meta=data.get("meta", {}),
        elements=elements,
    )
