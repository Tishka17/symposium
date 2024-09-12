from collections.abc import Callable

from symposium.core import (
    Renderer,
    RenderingContext,
)
from symposium.events import Click, WidgetClick
from symposium.handle import FunctionalHandler
from symposium.render import Keyboard, KeyboardButton, extract_text
from ..core.router import BaseEventContext, RouteRegistry
from .base import BaseWidget


class Button(BaseWidget):
    def __init__(self, id: str, text: Renderer, on_click: Callable):
        super().__init__(id)
        self.on_click = on_click
        self.text = text

    async def handle(self, context: BaseEventContext) -> None:
        await self._emit(
            context,
            WidgetClick(
                data=None,
                source=self,
                parent_event=context.event,
            ),
        )

    def register(self, router: RouteRegistry) -> None:
        router.add_handler(self._filter, self)
        router.add_handler(
            self._filter_click,
            FunctionalHandler(self.on_click),
        )

    def _filter_click(self, context: BaseEventContext) -> bool:
        if not isinstance(context.event, WidgetClick):
            return False
        return context.event.source is self

    def _filter(self, context: BaseEventContext) -> bool:
        if not isinstance(context.event, Click):
            return False
        return context.event.data == self.id

    async def _render_single(
        self,
        rendering_context: RenderingContext,
    ) -> Keyboard:
        btn = KeyboardButton(
            text=extract_text(await self.text.render(rendering_context)),
            data=self.id,
        )
        return Keyboard([[btn]])
