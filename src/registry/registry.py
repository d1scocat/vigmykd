from controller.consumers.input_consumer import InputConsumer
from controller.input_model import Mutation
from view.adapter import ViewAdapter
from scene.router import SceneInputRouter
from registry.abstract import AbstractClassRegistry, \
    AbstractNamedRegistry, AbstractRegistry

from typing import Any, TypeVar

import pkgutil
import importlib


class ConsumerRegistry(AbstractClassRegistry[InputConsumer]):
    def __init__(self):
        super().__init__()

    def discover(self):
        import controller.consumers as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")

    def router_by_tag(self, tag: str) -> SceneInputRouter:
        return SceneInputRouter(self.filter(tag))


class InputMutatorRegistry(AbstractNamedRegistry[Mutation]):
    def __init__(self):
        super().__init__()

    def discover(self):
        import controller.mutators as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")


VAT = TypeVar("VAT")


class ViewAdapterRegistry(AbstractRegistry):
    def __init__(self):
        self._adapters: dict[type[Any], ViewAdapter[Any]] = {}

    def discover(self):
        import view.adapter as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")

    def init_all(self):
        pass  # no-op

    def register(self, obj_type: type[VAT], adapter: ViewAdapter[VAT]):
        self._adapters[obj_type] = adapter

    def __getitem__(self, obj_type: type[VAT]) -> ViewAdapter[VAT] | None:
        return self._adapters.get(obj_type)


class GlobalRegistries:
    _accepting_registrations: bool = True
    consumers: ConsumerRegistry
    mutators: InputMutatorRegistry
    view_adapters: ViewAdapterRegistry

    initable_registries: list[AbstractRegistry]

    def __init__(self) -> None:
        self.registries: list[AbstractRegistry] = []

        self.consumers = ConsumerRegistry()
        self.mutators = InputMutatorRegistry()
        self.view_adapters = ViewAdapterRegistry()

        self.initable_registries = [
            self.consumers,
            self.mutators,
            self.view_adapters
        ]

    def init_all(self):
        for registry in self:
            registry.discover()
            registry.init_all()
        self._freeze()

    def _freeze(self):
        self._accepting_registrations = False

    def _unfreeze(self):
        self._accepting_registrations = True

    def is_frozen(self):
        return not self._accepting_registrations

    def __iter__(self):
        return iter(self.initable_registries)


registries = GlobalRegistries()


def raise_on_frozen():
    if registries.is_frozen():
        raise ValueError("The registry is not accepting new registrations")


def register_consumer(tags: list[str] | None):
    raise_on_frozen()

    def wrapper(cls: type[InputConsumer]):
        registries.consumers.register(cls, tags)
        return cls
    return wrapper


def register_mutator(name: str):
    raise_on_frozen()

    def wrapper(func: Mutation):
        registries.mutators.register(name, func, [])
        return func
    return wrapper


def register_adapter(target_type: type[VAT]):
    raise_on_frozen()

    def wrapper(cls: type[ViewAdapter[VAT]]):
        registries.view_adapters.register(target_type, cls())
        return cls
    return wrapper
