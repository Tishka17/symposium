import asyncio
import os

from telebot.async_telebot import AsyncTeleBot

from dialogs import window, simple
from symposium.integrations.telebot import to_telebot, MessageManager, register_handler, render_telebot
from symposium.integrations.telebot_states import setup_dialogs


async def sender(bot, chat_id, result):
    message_manager = MessageManager(bot)
    sent = await message_manager.send(
        chat_id,
        to_telebot(result),
    )
    print("SENT", sent)


async def main():
    bot = AsyncTeleBot(token=os.getenv("BOT_TOKEN"))
    message_manager = MessageManager(bot)
    registry, factory = setup_dialogs(bot)
    bot.factory = factory
    bot.sender = sender
    registry.include(window)

    register_handler(simple, bot)
    rendered = await render_telebot(simple)

    await message_manager.send(
        chat_id=int(os.getenv("CHAT_ID")),
        data=rendered,
    )

    await bot.infinity_polling()


asyncio.run(main())
