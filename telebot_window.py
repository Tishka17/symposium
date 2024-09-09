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
from symposium.windows.state import State, StatesGroup
from symposium.windows.widget_context import StatefulEventContext, StatefulRenderingContext
from symposium.windows.window import Window


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

    assert isinstance(context, StatefulEventContext)
    await context.transition_manager.start(MainSG.start)

    rendering_context = StatefulRenderingContext(
        chat_key=context.chat_key,
        ui_root=window,
        framework_data=context.framework_data,
        data={},
        cache={},
        context=context.transition_manager._context,
        transition_manager=context.transition_manager,
        stack=context.stack,
    )

    res = await window.render(rendering_context)
    res = add_context_id(res, rendering_context)
    print("RENDERED", res)

    bot = context.framework_data["bot"]

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
    registry = setup_dialogs(bot)
    registry.include(window)

    symposium_router = registry.router
    symposium_router.add_handler(filter_widget_click, on_any_widget_click)
    simple.register(symposium_router)

    rendered = await render_telebot(simple)

    await message_manager.send(
        chat_id=1,
        data=rendered,
    )

    await bot.infinity_polling()


asyncio.run(main())
