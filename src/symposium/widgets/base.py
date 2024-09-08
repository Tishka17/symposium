from dataclasses import replace
from typing import Any, Awaitable, Callable

from symposium.core import (
    EventContext,
    Handler,
    Renderer,
    RenderingContext,
    RenderingResult,
    Router,
)
from symposium.core.finder import Finder
from symposium.handle import HandlerHolder

DataGetter = Callable[[RenderingContext], Awaitable[dict]]


class BaseWidget(Finder, Renderer, HandlerHolder, Handler):
    def __init__(
            self,
            id: str | None = None,
            getter: DataGetter | None = None,
    ):
        self.id = id
        self.getter = getter

    def find(self, widget_id: str) -> Any:
        if widget_id == self.id:
            return self
        return None

    async def _emit(self, old_context: EventContext, event: Any) -> bool:
        context = replace(old_context, event=event)
        handler = context.router.prepare_handlers(context)
        if not handler:
            return False
        await handler.handle(context)
        return True

    async def handle(self, context: EventContext) -> None:
        pass

    def register(self, router: Router) -> None:
        pass

    async def render(
            self,
            rendering_context: RenderingContext,
    ) -> RenderingResult:
        # TODO when condition
        if self.getter:
            data = await self.getter(rendering_context)
            rendering_context = replace(
                rendering_context,
                data=rendering_context.data | data,
            )

        res = await self._render(rendering_context)
        if res is not NotImplemented:
            return res
        res = await self._render_single(rendering_context)
        if res is not NotImplemented:
            return RenderingResult([res])
        return RenderingResult([])

    async def _render(
            self,
            rendering_context: RenderingContext,
    ) -> RenderingResult:
        return NotImplemented

    async def _render_single(
            self,
            rendering_context: RenderingContext,
    ) -> Any:
        return NotImplemented
