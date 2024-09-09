from typing import Any

from telebot import ContinueHandling
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    CallbackQuery,
)

from symposium.integrations.telegram_base import ChatContext, TelegramHandler
from symposium.router import SimpleRouter
from symposium.windows.memory_storage import MemoryStorage
from symposium.windows.registry import DialogRegistry


class TelebotHandlerAdapter:
    def __init__(self, telegram_handler: TelegramHandler, bot: AsyncTeleBot):
        super().__init__()
        self.telegram_handler = telegram_handler
        self.bot = bot


    async def handle_callback(
            self,
            event: CallbackQuery,
            **kwargs: Any,
    ) -> Any:
        if not isinstance(event, CallbackQuery):
            return ContinueHandling

        chat_context = ChatContext(
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            thread_id=event.message.message_thread_id,
            business_connection_id=event.message.business_connection_id,
        )
        kwargs["bot"] = self.bot
        if not await self.telegram_handler.handle_click(
                callback_data=event.data,
                chat_context=chat_context,
                framework_data=kwargs,
                event=event,
        ):
            return ContinueHandling


def setup_dialogs(bot: AsyncTeleBot) -> DialogRegistry:
    symposium_router = SimpleRouter()
    registry = DialogRegistry(symposium_router)

    telegram_handler = TelegramHandler(symposium_router, MemoryStorage(), registry)
    adapter = TelebotHandlerAdapter(telegram_handler, bot)
    bot.register_callback_query_handler(
        adapter.handle_callback,
        lambda event: True,
    )
    return registry
