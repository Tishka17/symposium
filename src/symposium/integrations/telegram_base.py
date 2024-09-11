from dataclasses import dataclass
from typing import Any

from symposium.core import RenderingResult, Router
from symposium.events import Click
from symposium.render import Keyboard, KeyboardButton
from symposium.windows.manager_factory import ManagerFactory
from symposium.windows.protocols.storage import (
    ContextQuery,
    SpecialIds,
)
from symposium.windows.widget_context import (
    StatefulRenderingContext,
)


@dataclass(frozen=True)
class ChatContext:
    chat_id: int
    user_id: int
    thread_id: int | None
    business_connection_id: str | None


CONTEXT_ID_SEP = "\x1d"


def add_context_id(
    result: RenderingResult,
    context: StatefulRenderingContext,
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
                ],
            )
        new_items.append(item)
    return RenderingResult(items=new_items)


class TelegramHandler:
    def __init__(
        self,
        router: Router,
        factory: ManagerFactory,
    ):
        super().__init__()
        self._factory = factory
        self._router = router

    async def handle_click(
        self,
        callback_data: str,
        chat_context: Any,
        event: Any,
        framework_data: Any,
    ):
        if CONTEXT_ID_SEP in callback_data:
            context_id, callback_data = callback_data.split(
                CONTEXT_ID_SEP,
                maxsplit=1,
            )
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

        manager = await self._factory.manager(query)
        click = manager.event_context(
            event=Click(
                data=callback_data,
                parent_event=event,
            ),
            router=self._router,
            framework_data=framework_data,
        )
        print("handle")
        res = await self._router.handle(click)
        print("handle", res)
        return res
