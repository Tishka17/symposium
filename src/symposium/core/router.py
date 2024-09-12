from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from .context import BaseContext
from .events import SymposiumEvent


@dataclass(frozen=True, kw_only=True)
class BaseEventContext(BaseContext):
    event: SymposiumEvent
    router: "Router"


class Filter(Protocol):
    @abstractmethod
    def __call__(self, context: BaseEventContext) -> bool:
        raise NotImplementedError


class Handler(Protocol):
    @abstractmethod
    async def handle(self, context: BaseEventContext) -> None:
        raise NotImplementedError


class RouteRegistry(Protocol):
    @abstractmethod
    def add_handler(self, filter: Filter, handler: Handler) -> None:
        raise NotImplementedError


class Router(Protocol):
    @abstractmethod
    def prepare_handlers(self, event: BaseEventContext) -> Handler | None:
        raise NotImplementedError

    @abstractmethod
    async def handle(self, event: BaseEventContext) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True)
class EventContext(BaseContext):
    event: SymposiumEvent
    router: Router
