from registry.abstract.abstract import AbstractRegistry

from typing import Dict, Generic, List, Type, TypeVar


T = TypeVar("T")


class AbstractClassRegistry(AbstractRegistry, Generic[T]):
    def __init__(self):
        self._classes: List[Type[T]] = []
        self.objects: List[T] = []
        self._tagged_classes: Dict[str, List[Type[T]]] = {}
        self._tagged_objects: Dict[str, List[T]] = {}

    def register(self, cls: Type[T], tags: List[str] | None = None):
        if cls not in self._classes:
            self._classes.append(cls)

        if tags is not None:
            for tag in tags:
                self._tagged_classes.setdefault(tag, [])
                if cls not in self._tagged_classes[tag]:
                    self._tagged_classes[tag].append(cls)

    def init_all(self, *args, **kwargs):
        if self.objects:
            return

        for cls in self._classes:
            obj = cls(*args, **kwargs)
            tags = [k for k, v in self._tagged_classes.items() if cls in v]

            for tag in tags:
                self._tagged_objects.setdefault(tag, []).append(obj)

            self.objects.append(obj)

    def filter(self, tag: str) -> List[T]:
        return self._tagged_objects.get(tag, [])

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        return iter(self.objects)
