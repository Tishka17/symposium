from symposium.events import Click
from symposium.handle import Handler, Router, EventContext
from symposium.render import Renderer, RenderingContext, RenderingResult, Keyboard, KeyboardButton


class Button(Handler, Renderer):
    def __init__(self, id: str):
        self.id = id

    def handle(self, context: EventContext) -> bool:
        print("Click detected")
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
