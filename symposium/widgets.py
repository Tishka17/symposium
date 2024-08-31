from symposium.events import Click
from symposium.handle import Router, EventContext, HandlingWidget
from symposium.render import Renderer, RenderingContext, RenderingResult, Keyboard, KeyboardButton, Text


class Button(HandlingWidget, Renderer):
    def __init__(self, id: str):
        self.id = id

    async def handle(self, context: EventContext) -> bool:
        print("Click detected")
        await context.event.parent_event.answer("Click detected")
        return False

    def register(self, router: Router) -> None:
        router.add_handler(self._filter, self)

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
