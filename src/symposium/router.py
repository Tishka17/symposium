from dataclasses import dataclass

from symposium.core import EventContext, Filter, Handler, Router
from .handle import MetaHandler


@dataclass
class _RouterItem:
    filter: Filter
    handler: Handler


class SimpleRouter(Router):
    def __init__(self):
        self.handlers: list[_RouterItem] = []

    def add_handler(self, filter: Filter, handler: Handler) -> None:
        self.handlers.append(_RouterItem(filter, handler))

    def prepare_handlers(self, event: EventContext) -> Handler | None:
        handlers = []
        for item in self.handlers:
            if item.filter(event):
                handlers.append(item.handler)
        if handlers:
            return MetaHandler(handlers)
        return None

    async def handle(self, event: EventContext) -> bool:
        handler = self.prepare_handlers(event)
        if not handler:
            return False
        await handler.handle(event)
        return True
