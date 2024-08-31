from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, Callable, Awaitable



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


class HandlerHolder(Protocol):
    @abstractmethod
    def register(self, router: Router) -> None:
        raise NotImplementedError


class FunctionalHandler(Handler):
    def __init__(self, callback: Callable[[EventContext], Awaitable[bool]]) -> None:
        self.callback = callback

    async def handle(self, context: EventContext) -> bool:
        return await self.callback(context)


async def emit(context: EventContext) -> None:
    handler = context.router.prepare_handlers(context)
    await handler.handle(context)