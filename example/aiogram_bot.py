import asyncio
import os

from aiogram import Bot, Dispatcher

from dialogs import window, simple
from symposium.integrations.aiogram import render_aiogram, MessageManager, register_handler
from symposium.integrations.aiogram_states import setup_dialogs


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    registry, factory = setup_dialogs(dp)
    bot.factory = factory
    bot.message_manager = MessageManager(bot)
    registry.include(window)

    register_handler(simple, dp)
    rendered = await render_aiogram(simple)

    await bot.message_manager.send(
        chat_id=int(os.getenv("CHAT_ID")),
        data=rendered,
    )

    await dp.start_polling(bot)


asyncio.run(main())
