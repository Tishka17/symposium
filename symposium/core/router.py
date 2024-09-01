from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, Any


@dataclass
class EventContext:
    event: Any
    router: "Router"


class Filter(Protocol):
    @abstractmethod
    def __call__(self, context: EventContext) -> bool:
        raise NotImplementedError


class Router(Protocol):
    @abstractmethod
    def add_handler(self, filter: Filter, handler: "Handler") -> None:
        raise NotImplementedError

    @abstractmethod
    def prepare_handlers(self, event: EventContext) -> "Handler | None":
        raise NotImplementedError


class Handler(Protocol):
    @abstractmethod
    async def handle(self, context: EventContext) -> bool:
        raise NotImplementedError
