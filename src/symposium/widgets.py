from collections.abc import Callable
from dataclasses import replace
from typing import Any

from symposium.core import (
    EventContext,
    Handler,
    Renderer,
    RenderingContext,
    RenderingResult,
    Router,
)
from symposium.core.finder import Finder
from symposium.events import Click, WidgetClick
from symposium.handle import FunctionalHandler, HandlerHolder
from symposium.render import Keyboard, KeyboardButton, Text, extract_text


class BaseWidget(Finder, Renderer, HandlerHolder, Handler):
    def __init__(self, id: str | None = None):
        self.id = id

    def find(self, widget_id: str) -> Any:
        if widget_id == self.id:
            return self
        return None

    async def _emit(self, old_context: EventContext, event: Any) -> None:
        context = replace(old_context, event=event)
        handler = context.router.prepare_handlers(context)
        await handler.handle(context)

    async def handle(self, context: EventContext) -> None:
        pass

    def register(self, router: Router) -> None:
        pass

    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        return RenderingResult([])

    def _rendered_single(self, item: Any) -> RenderingResult:
        return RenderingResult(items=[item])


class Button(BaseWidget):
    def __init__(self, id: str, text: Renderer, on_click: Callable):
        super().__init__(id)
        self.on_click = on_click
        self.text = text

    async def handle(self, context: EventContext) -> None:
        await self._emit(
            context,
            WidgetClick(
                data=None,
                source=self,
                parent_event=context.event,
            ),
        )

    def register(self, router: Router) -> None:
        router.add_handler(self._filter, self)
        router.add_handler(
            self._filter_click,
            FunctionalHandler(self.on_click),
        )

    def _filter_click(self, context: EventContext) -> bool:
        if not isinstance(context.event, WidgetClick):
            return False
        return context.event.source is self

    def _filter(self, context: EventContext) -> bool:
        if not isinstance(context.event, Click):
            return False
        return context.event.data == self.id

    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        btn = KeyboardButton(
            text=extract_text(await self.text.render(rendering_context)),
            data=self.id,
        )
        return self._rendered_single(Keyboard([[btn]]))


class Format(BaseWidget):
    def __init__(self, text: str, id: str | None = None):
        super().__init__(id)
        self.text = text

    def register(self, router: Router) -> None:
        pass

    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        rendered_text = self.text.format_map(
            rendering_context.data,
        )
        return self._rendered_single(Text(text=rendered_text, entities=None))


class Group(BaseWidget):
    def __init__(self, *widgets, id: str | None = None):
        super().__init__(id)
        self.widgets = widgets

    def register(self, router: Router) -> None:
        for widget in self.widgets:
            widget.register(router)

    def find(self, widget_id: str) -> Any:
        for widget in self.widgets:
            if found := widget.find(widget_id):
                return found
        return super().find(widget_id)

    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        if rendering_context.ui_root is None:
            rendering_context = replace(rendering_context, ui_root=self)
        items = []
        for widget in self.widgets:
            widget_result = await widget.render(rendering_context)
            items.extend(widget_result.items)
        return RenderingResult(items)
