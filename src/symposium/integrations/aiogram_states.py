from typing import Any

from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import (
    CallbackQuery,
    TelegramObject,
)

from symposium.core import RenderingContext, RenderingResult
from symposium.integrations.aiogram import to_aiogram
from symposium.integrations.telegram_base import (
    ChatContext,
    TelegramHandler,
    add_context_id,
)
from symposium.router import SimpleRouter
from symposium.windows.impl.memory_storage import MemoryStorage
from symposium.windows.manager_factory import ManagerFactory
from symposium.windows.protocols.window_sender import WindowSender
from symposium.windows.registry import DialogRegistry


class AiogramRouterAdapter(AiogramRouter):
    def __init__(self, telegram_handler: TelegramHandler):
        super().__init__()
        self.telegram_handler = telegram_handler

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

        chat_context = ChatContext(
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            thread_id=event.message.message_thread_id,
            business_connection_id=event.message.business_connection_id,
        )
        if not await self.telegram_handler.handle_click(
            callback_data=event.data,
            chat_context=chat_context,
            framework_data=kwargs,
            event=event,
        ):
            return UNHANDLED


class Sender(WindowSender):
    async def send(
        self, data: RenderingResult, context: RenderingContext
    ) -> None:
        bot = context.framework_data["bot"]
        data = add_context_id(data, context)
        res = to_aiogram(data)
        await bot.send_message(
            chat_id=context.chat_key.chat_id,
            text=res.text,
            reply_markup=res.reply_markup,
        )


def setup_dialogs(
    router: AiogramRouter,
) -> tuple[DialogRegistry, ManagerFactory]:
    symposium_router = SimpleRouter()
    registry = DialogRegistry(symposium_router)
    factory = ManagerFactory(
        router=symposium_router,
        registry=registry,
        storge=MemoryStorage(),
        window_sender=Sender(),
    )
    telegram_handler = TelegramHandler(symposium_router, factory)
    adapter = AiogramRouterAdapter(telegram_handler)
    router.include_router(adapter)
    return registry, factory
