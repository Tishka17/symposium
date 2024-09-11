import asyncio
import os

from telebot.async_telebot import AsyncTeleBot

from symposium.core import RenderingContext
from symposium.events import WidgetClick
from symposium.handle import EventContext, FunctionalHandler
from symposium.integrations.telebot import telebot_event, render_telebot, MessageManager, to_telebot
from symposium.integrations.telebot_states import setup_dialogs
from symposium.integrations.telegram_base import add_context_id
from symposium.widgets.group import Group
from symposium.widgets.keyboard import Button
from symposium.widgets.text import Format
from symposium.windows.manager_factory import ManagerFactory
from symposium.windows.protocols.storage import ContextQuery, SpecialIds
from symposium.windows.state import State, StatesGroup
from symposium.windows.window import Window
from symposium.integrations.telebot import register_handler


async def getter(context: RenderingContext) -> dict:
    return {"name": "Tishka17"}


async def on_click(context: EventContext):
    print("Click detected")
    callback = telebot_event(context)


def filter_widget_click(context: EventContext):
    return isinstance(context.event, WidgetClick)


@FunctionalHandler
async def on_any_widget_click(context: EventContext):
    print("Any click")


class MainSG(StatesGroup):
    start = State()


window = Window(
    Format("Window hello, {name}"),
    Button(
        text=Format("Click me!"),
        id="y",
        on_click=on_click,
    ),
    getter=getter,
    state=MainSG.start,
)


async def on_simple_click(context: EventContext):
    callback = telebot_event(context)
    bot = context.framework_data["bot"]
    factory: ManagerFactory = bot.factory
    print("on_simple_click")
    manager = await factory.manager(
        query=ContextQuery(
            chat=context.chat_key,
            stack_id="",
            context_id=SpecialIds.AUTO,
        ),
    )
    await manager.start(MainSG.start)
    rendering_context = manager.rendering_context(context.framework_data)
    res = await window.render(rendering_context)
    res = add_context_id(res, rendering_context)
    print("RENDERED", res)

    message_manager = MessageManager(bot)
    sent = await message_manager.send(
        context.chat_key.chat_id,
        to_telebot(res),
    )
    print("SENT", sent)


simple = Group(
    Format("Simple hello, {name}"),
    Button(
        text=Format("Click me!"),
        id="x",
        on_click=on_simple_click,
    ),
    getter=getter,
)


async def main():
    bot = AsyncTeleBot(token=os.getenv("BOT_TOKEN"))
    message_manager = MessageManager(bot)
    registry, factory = setup_dialogs(bot)
    bot.factory = factory
    registry.include(window)

    register_handler(simple, bot)
    rendered = await render_telebot(simple)

    await message_manager.send(
        chat_id=1,
        data=rendered,
    )

    await bot.infinity_polling()


asyncio.run(main())
