from abc import abstractmethod
from collections.abc import Awaitable, Callable
from typing import Protocol

from symposium.core import EventContext, Handler, Router


class HandlerHolder(Protocol):
    @abstractmethod
    def register(self, router: Router) -> None:
        raise NotImplementedError


class MetaHandler(Handler):
    def __init__(self, handlers: list[Handler]) -> None:
        self.handlers = handlers

    async def handle(self, event: EventContext) -> None:
        for handler in self.handlers:
            await handler.handle(event)


class FunctionalHandler(Handler):
    def __init__(
        self,
        callback: Callable[[EventContext], Awaitable[bool]],
    ) -> None:
        self.callback = callback

    async def handle(self, context: EventContext) -> bool:
        return await self.callback(context)
