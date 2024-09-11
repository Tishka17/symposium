import asyncio
import os

from aiogram import Bot, Dispatcher

from dialogs import window, simple
from symposium.integrations.aiogram import render_aiogram, MessageManager, register_handler, to_aiogram
from symposium.integrations.aiogram_states import setup_dialogs


async def sender(bot, chat_id, result):
    message_manager = MessageManager(bot)
    sent = await message_manager.send(
        chat_id,
        to_aiogram(result),
    )
    print("SENT", sent)


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    message_manager = MessageManager(bot)
    dp = Dispatcher()
    registry, factory = setup_dialogs(dp)
    bot.factory = factory
    bot.sender = sender
    registry.include(window)

    register_handler(simple, dp)
    rendered = await render_aiogram(simple)

    await message_manager.send(
        chat_id=int(os.getenv("CHAT_ID")),
        data=rendered,
    )

    await dp.start_polling(bot)


asyncio.run(main())
