from registry.abstract.abstract import AbstractRegistry

from typing import Generic, TypeVar


T = TypeVar("T")


class AbstractClassRegistry(AbstractRegistry, Generic[T]):
    def __init__(self):
        self._classes: list[type[T]] = []
        self.objects: list[T] = []
        self._tagged_classes: dict[str, list[type[T]]] = {}
        self._tagged_objects: dict[str, list[T]] = {}

    def register(self, cls: type[T], tags: list[str] | None = None):
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

    def filter(self, tag: str) -> list[T]:
        return self._tagged_objects.get(tag, [])

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        return iter(self.objects)
