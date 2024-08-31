from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class EventContext:
    event: Any


class Filter(Protocol):
    @abstractmethod
    def __call__(self, context: EventContext) -> bool:
        raise NotImplementedError


class Router(Protocol):
    @abstractmethod
    def add_handler(self, filter: Filter, handler: "Handler") -> None:
        raise NotImplementedError


class Handler(Protocol):
    @abstractmethod
    def handle(self, context: EventContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def register(self, router: Router) -> None:
        raise NotImplementedError
