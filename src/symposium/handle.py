from abc import abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from symposium.core import Handler
from symposium.core.router import BaseEventContext, RouteRegistry


class HandlerHolder(Protocol):
    @abstractmethod
    def register(self, router: RouteRegistry) -> None:
        raise NotImplementedError


class MetaHandler(Handler):
    def __init__(self, handlers: list[Handler]) -> None:
        self.handlers = handlers

    async def handle(self, context: BaseEventContext) -> None:
        for handler in self.handlers:
            await handler.handle(context)


class FunctionalHandler(Handler):
    def __init__(
        self,
        callback: Callable[[BaseEventContext], Awaitable[Any]],
    ) -> None:
        self.callback = callback

    async def handle(self, context: BaseEventContext) -> None:
        await self.callback(context)
