from controller.consumers.input_consumer import InputConsumer
from controller import PlayerInput
from view.adapter import ViewAdapter

from registry.abstract import AbstractClassRegistry, \
    AbstractNamedRegistry, AbstractRegistry

from typing import Any, Callable, Dict, List, Type, TypeAlias, TypeVar

import pkgutil
import importlib


class ConsumerRegistry(AbstractClassRegistry[InputConsumer]):
    def __init__(self):
        super().__init__()

    def discover(self):
        import controller.consumers as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")


Mutation: TypeAlias = Callable[[PlayerInput], None]


class InputMutatorRegistry(AbstractNamedRegistry[Mutation]):
    def __init__(self):
        super().__init__()

    def discover(self):
        import controller.mutators as pkg
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{modname}")


VAT = TypeVar("VAT")


class ViewAdapterRegistry:
    def __init__(self):
        self._adapters: Dict[Type[Any], ViewAdapter[Any]] = {}
    
    def register(self, obj_type: Type[VAT], adapter: ViewAdapter[VAT]):
        self._adapters[obj_type] = adapter
    
    def __getitem__(self, obj_type: Type[VAT]) -> ViewAdapter[VAT] | None:
        return self._adapters.get(obj_type)


class GlobalRegistries:
    consumers: ConsumerRegistry
    mutators: InputMutatorRegistry
    view_adapters: ViewAdapterRegistry

    initable_registries: List[AbstractRegistry]

    def __init__(self) -> None:
        self.registries = []

        self.consumers = ConsumerRegistry()
        self.mutators = InputMutatorRegistry()
        self.view_adapters = ViewAdapterRegistry()

        self.initable_registries = [
            self.consumers,
            self.mutators
        ]

    def __iter__(self):
        return iter(self.initable_registries)


registries = GlobalRegistries()


def register_consumer(cls: Type[InputConsumer]):
    registries.consumers.register(cls)
    return cls


def register_mutator(name: str):
    def wrapper(func: Mutation):
        registries.mutators.register(name, func)
        return func
    return wrapper


def register_adapter(target_type: Type[VAT]):
    def wrapper(cls: Type[ViewAdapter[VAT]]):
        registries.view_adapters.register(target_type, cls())
        return cls
    return wrapper
