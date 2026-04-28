from abc import ABC, abstractmethod

from typing import TypeVar


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
