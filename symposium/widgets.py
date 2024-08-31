from collections.abc import Callable

from symposium.events import Click, WidgetClick
from symposium.handle import Router, EventContext, HandlingWidget, FunctionalHandler, emit
from symposium.render import Renderer, RenderingContext, RenderingResult, Keyboard, KeyboardButton, Text


class Button(HandlingWidget, Renderer):
    def __init__(self, id: str, on_click: Callable):
        self.id = id
        self.on_click = on_click

    async def handle(self, context: EventContext) -> bool:
        await emit(
            context=EventContext(
                event=WidgetClick(
                    data=None,
                    source=self,
                    parent_event=context.event,
                ),
                router=context.router,
            )
        )
        return False

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

    def render(self, rendering_context: RenderingContext) -> RenderingResult:
        return RenderingResult(
            items=[
                Keyboard([[KeyboardButton(
                    text="text",
                    data=self.id,
                )]]),
            ]
        )


class Format(Renderer):
    def __init__(self, text: str):
        self.text = text

    def register(self, router: Router) -> None:
        pass

    def render(self, rendering_context: RenderingContext) -> RenderingResult:
        rendered_text = self.text.format_map(
            rendering_context.data,
        )
        return RenderingResult(
            items=[Text(text=rendered_text, entities=None)]
        )


class Group(Renderer):
    def __init__(self, *widgets):
        self.widgets = widgets

    def register(self, router: Router) -> None:
        for widget in self.widgets:
            widget.register(router)

    def render(self, rendering_context: RenderingContext) -> RenderingResult:
        items = []
        for widget in self.widgets:
            items.extend(widget.render(rendering_context).items)
        return RenderingResult(items)
