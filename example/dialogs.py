from aiogram import Bot

from symposium.core import RenderingContext
from symposium.events import WidgetClick
from symposium.handle import EventContext, FunctionalHandler
from symposium.integrations.telegram_base import add_context_id
from symposium.widgets.group import Group
from symposium.widgets.keyboard import Button
from symposium.widgets.text import Format
from symposium.windows.manager_factory import ManagerFactory
from symposium.windows.protocols.storage import ContextQuery, SpecialIds
from symposium.windows.state import State, StatesGroup
from symposium.windows.window import Window


async def getter(context: RenderingContext) -> dict:
    return {"name": "Tishka17"}


async def on_click(context: EventContext):
    print("Click detected")
    bot: Bot = context.framework_data["bot"]
    await bot.send_message(
        chat_id=context.chat_key.chat_id,
        text="Window clicked"
    )


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
    bot = context.framework_data["bot"]
    manager = await bot.factory.manager(
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
    print("Chat", context.chat_key)

    # dirty hack
    sent = await bot.sender(
        bot,
        context.chat_key.chat_id,
        res,
    )



simple = Group(
    Format("Simple hello, {name}"),
    Button(
        text=Format("Click me!"),
        id="x",
        on_click=on_simple_click,
    ),
    getter=getter,
)
