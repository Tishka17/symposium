from typing import Any

from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import (
    CallbackQuery,
    TelegramObject,
)

from symposium.core import Router, RenderingResult
from symposium.events import Click
from symposium.integrations.telegram_base import ChatContext
from symposium.render import Keyboard, KeyboardButton
from symposium.router import SimpleRouter
from symposium.windows.memory_storage import MemoryStorage
from symposium.windows.registry import DialogRegistry
from symposium.windows.simple_manager import SimpleTransitionManager
from symposium.windows.storage import StackStorage, ContextQuery, SpecialIds
from symposium.windows.widget_context import StatefulEventContext, StatefulRenderingContext

CONTEXT_ID_SEP = "\x1D"


def add_intent_id(
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


class AiogramRouterAdapter(AiogramRouter):
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

    def resolve_used_update_types(
            self,
            skip_events: set[str] | None = None,
    ) -> list[str]:
        return ["callback"]

    async def propagate_event(
            self,
            update_type: str,
            event: TelegramObject,
            **kwargs: Any,
    ) -> Any:
        if not isinstance(event, CallbackQuery):
            return UNHANDLED
        callback_data = event.data
        if CONTEXT_ID_SEP not in callback_data:
            return UNHANDLED

        chat_context = ChatContext(
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            thread_id=event.message.message_thread_id,
            business_connection_id=event.message.business_connection_id,
        )

        context_id, data = callback_data.split(CONTEXT_ID_SEP, maxsplit=1)
        stack, context = self.storge.load_locked(ContextQuery(
            stack_id=SpecialIds.AUTO,
            context_id=context_id,
            chat=chat_context,
        ))

        manager = SimpleTransitionManager(
            context=context,
            stack=stack,
            registry=self.registry,
        )
        click = StatefulEventContext(
            event=Click(
                data=data,
                parent_event=event,
            ),
            context=context,
            stack=stack,
            transition_manager=manager,
            router=self.router,
            ui_root=manager,
            framework_data=kwargs,
            chat_key=chat_context,
        )
        handler = self.router.prepare_handlers(click)
        if not handler:
            return UNHANDLED
        await handler.handle(click)


def setup_dialogs(router: AiogramRouter) -> Router:
    symposium_router = SimpleRouter()
    registry = DialogRegistry(symposium_router)

    adapter = AiogramRouterAdapter(symposium_router, MemoryStorage(), registry)
    router.include_router(adapter)
    return registry
