from dataclasses import dataclass
from typing import Any

from symposium.core import Router, RenderingResult
from symposium.events import Click
from symposium.render import Keyboard, KeyboardButton
from symposium.windows.registry import DialogRegistry
from symposium.windows.simple_manager import SimpleTransitionManager
from symposium.windows.storage import StackStorage, ContextQuery, SpecialIds
from symposium.windows.widget_context import StatefulRenderingContext, StatefulEventContext


@dataclass(frozen=True)
class ChatContext:
    chat_id: int
    user_id: int
    thread_id: int | None
    business_connection_id: str | None


CONTEXT_ID_SEP = "\x1D"


def add_context_id(
        result: RenderingResult, context: StatefulRenderingContext,
) -> RenderingResult:
    new_items = []
    for item in result.items:
        if isinstance(item, Keyboard):
            item = Keyboard(
                buttons=[
                    [
                        KeyboardButton(
                            data=f"{context.context.id}{CONTEXT_ID_SEP}{button.data}",
                            text=button.text,
                        )
                        if isinstance(button, KeyboardButton)
                        else button
                        for button in row
                    ]
                    for row in item.buttons
                ]
            )
        new_items.append(item)
    return RenderingResult(items=new_items)


class TelegramHandler:
    def __init__(
            self,
            router: Router,
            storge: StackStorage,
            registry: DialogRegistry,
    ):
        super().__init__()
        self.router = router
        self.storge = storge
        self.registry = registry

    async def handle_click(
            self,
            callback_data: str,
            chat_context: Any,
            event: Any,
            framework_data: Any,
    ):

        if CONTEXT_ID_SEP in callback_data:
            context_id, callback_data = callback_data.split(CONTEXT_ID_SEP, maxsplit=1)
            query = ContextQuery(
                stack_id=SpecialIds.AUTO,
                context_id=context_id,
                chat=chat_context,
            )
        else:
            query = ContextQuery(
                stack_id="",  # default
                context_id=SpecialIds.AUTO,
                chat=chat_context,
            )

        stack, context = await self.storge.load_locked(query)

        manager = SimpleTransitionManager(
            chat=chat_context,
            context=context,
            stack=stack,
            registry=self.registry,
            storage=self.storge,
        )
        click = StatefulEventContext(
            event=Click(
                data=callback_data,
                parent_event=event,
            ),
            context=context,
            stack=stack,
            transition_manager=manager,
            router=self.router,
            ui_root=manager,
            framework_data=framework_data,
            chat_key=chat_context,
        )
        handler = self.router.prepare_handlers(click)
        if not handler:
            return False
        await handler.handle(click)
        return True