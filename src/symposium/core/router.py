from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from .finder import Finder


@dataclass(frozen=True, kw_only=True)
class EventContext:
    event: Any
    router: "Router"
    ui_root: Finder | None
    framework_data: Any = None
    chat_key: Any


class Filter(Protocol):
    @abstractmethod
    def __call__(self, context: EventContext) -> bool:
        raise NotImplementedError


class Handler(Protocol):
    @abstractmethod
    async def handle(self, context: EventContext) -> None:
        raise NotImplementedError


class Router(Protocol):
    @abstractmethod
    def add_handler(self, filter: Filter, handler: Handler) -> None:
        raise NotImplementedError

    @abstractmethod
    def prepare_handlers(self, event: EventContext) -> Handler | None:
        raise NotImplementedError
