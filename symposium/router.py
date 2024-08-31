from dataclasses import dataclass

from .handle import EventContext, Handler, Filter


@dataclass
class RouterItem:
    filter: Filter
    handler: Handler


class MetaHandler(Handler):
    def __init__(self, handlers: list[Handler]) -> None:
        self.handlers = handlers

    async def handle(self, event: EventContext) -> bool:
        for handler in self.handlers:
            await handler.handle(event)
        return True


class SimpleRouter:
    def __init__(self):
        self.handlers: list[RouterItem] = []

    def add_handler(self, filter: Filter, handler: Handler) -> None:
        self.handlers.append(RouterItem(filter, handler))

    def prepare_handlers(self, event: EventContext) -> Handler | None:
        handlers = []
        for item in self.handlers:
            if item.filter(event):
                handlers.append(item.handler)
        if handlers:
            return MetaHandler(handlers)
        return None
