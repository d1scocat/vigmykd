from typing import Any, Dict, List

from ui.components import button, component, container, image, page, \
    textarea


def build_component(obj: Dict[str, Any]) -> component.UIComponent:
    type = obj["type"].lower()

    id = obj["id"]
    z_index = obj.get("z_index", 0)
    position = obj["position"]
    size = obj["size"]
    texture = obj.get("texture", None)


    match type:
        case "image":
            return image.UIImage(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture
            )

        case "button", "btn":
            return button.UIButton(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                states=obj.get("states", {}),
                action=obj["action"],
                text=obj.get("text")
            )

        case "form", "container":
            children = [build_component(child) for child in obj.get("children", [])]
            return container.UIContainer(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture,
                children=children,
                states=obj.get("states")
            )

        case "textarea":
            return textarea.UITextArea(
                id=id,
                z_index=z_index,
                position=position,
                size=size,
                texture=texture,
                label=obj["label"],
                hint=obj["hint"]
            )

        case _:
            raise ValueError("Undefined component type", type, "with id", id)

def deserialize_into_ui(data: Dict[str, Any]) -> page.UIPage:
    elements = [build_component(elem) for elem in data["elements"]]
    return page.UIPage(
        id=data["id"],
        meta=data.get("meta", {}),
        elements=elements,
    )
