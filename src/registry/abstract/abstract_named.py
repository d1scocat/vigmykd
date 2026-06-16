from registry.abstract.abstract import AbstractRegistry

from typing import Generic, TypeVar


T = TypeVar("T")


class AbstractNamedRegistry(AbstractRegistry, Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}
        self._tags: dict[str, list[T]] = {}

    def register(self, name: str, value: T, tags: list[str] | None):
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

    def filter(self, tag: str) -> list[T]:
        return self._tags.get(tag, [])

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())
