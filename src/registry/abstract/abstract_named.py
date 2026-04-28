from registry.abstract.abstract import AbstractRegistry

from typing import Dict, Generic, List, TypeVar


T = TypeVar("T")


class AbstractNamedRegistry(AbstractRegistry, Generic[T]):
    def __init__(self) -> None:
        self._items: Dict[str, T] = {}
        self._tags: Dict[str, List[T]] = {}

    def register(self, name: str, value: T, tags: List[str] | None):
        print("Registering name", name, " and tags", tags)
        self._items[name] = value

        if tags is not None:
            for tag in tags:
                self._tags.setdefault(tag, [])
                if value not in self._tags[tag]:
                    self._tags[tag].append(value)

    def __getitem__(self, key: str) -> T | None:
        return self._items.get(key)

    def init_all(self, *args, **kwargs):
        pass  # no-op

    def filter(self, tag: str) -> List[T]:
        print("Filtering for tag", tag, "| Have tags:", self._tags.keys())
        return self._tags.get(tag, [])

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())
