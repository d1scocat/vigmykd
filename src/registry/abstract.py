from abc import ABC, abstractmethod

from typing import Dict, Generic, List, Type, TypeVar


T = TypeVar("T")


class AbstractRegistry(ABC):
    @abstractmethod
    def discover(self):
        """
        Imports ("discovers") all relevant objects that contain
        registration decorators.

        Implementation example:

        ```python
        import mypackage.storage as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")
        ```
        """
        pass

    @abstractmethod
    def init_all(self, *args, **kwargs):
        pass


class AbstractClassRegistry(AbstractRegistry, Generic[T]):
    def __init__(self):
        self._classes: List[Type[T]] = []
        self.objects: List[T] = []

    def register(self, cls: Type[T]):
        if cls not in self._classes:
            self._classes.append(cls)

    def init_all(self, *args, **kwargs):
        if self.objects:
            return
        self.objects = [cls(*args, **kwargs) for cls in self._classes]

    def __iter__(self):
        for val in self.objects:
            yield val


class AbstractNamedRegistry(AbstractRegistry, Generic[T]):
    def __init__(self) -> None:
        self._items: Dict[str, T] = {}

    def register(self, name: str, value: T):
        self._items[name] = value

    def __getitem__(self, key: str) -> T | None:
        return self._items.get(key)

    def init_all(self, *args, **kwargs):
        pass  # no-op

    def __iter__(self):
        return iter(self._items.values())
