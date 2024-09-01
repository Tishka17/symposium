import asyncio
import os

from telebot.async_telebot import AsyncTeleBot

from symposium.core import RenderingContext
from symposium.events import WidgetClick
from symposium.handle import EventContext, FunctionalHandler
from symposium.integrations.telebot import render_telebot, telebot_event, MessageManager, register_handler
from symposium.widgets import Button, Format
from symposium.windows.window import GetterGroup


async def getter(context: RenderingContext) -> dict:
    return {"name": "Tishka17"}


async def on_click(context: EventContext):
    print("Click detected")
    callback = telebot_event(context)
    # await callback.answer("Click detected")


def filter_widget_click(context: EventContext):
    return isinstance(context.event, WidgetClick)


@FunctionalHandler
async def on_any_widget_click(context: EventContext):
    print("Any click")


window = GetterGroup(
    Format("Hello, {name}"),
    Button(
        text=Format("Click me!"),
        id="x",
        on_click=on_click,
    ),
    getter=getter,
)


async def main():
    bot = AsyncTeleBot(token=os.getenv("BOT_TOKEN"))
    message_manager = MessageManager(bot)
    router = register_handler(window, bot)
    router.add_handler(filter_widget_click, on_any_widget_click)

    rendered = await render_telebot(window)

    await message_manager.send(
        chat_id=1,
        data=rendered,
    )
    await bot.infinity_polling()


asyncio.run(main())
