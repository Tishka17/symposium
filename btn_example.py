import asyncio
import os

from aiogram import Bot, Dispatcher

from symposium.aiogram import AiogramRouterAdapter, render_aiogram, aiogram_event
from symposium.events import WidgetClick
from symposium.handle import EventContext, FunctionalHandler
from symposium.render import RenderingContext
from symposium.widgets import Button, Group, Format


async def on_click(context: EventContext):
    print("Click detected")
    callback = aiogram_event(context)
    await callback.answer("Click detected")


def filter_widget_click(context: EventContext):
    return isinstance(context.event, WidgetClick)


@FunctionalHandler
async def on_any_widget_click(context: EventContext):
    print("Any click")


window = Group(
    Format("Hello, {name}"),
    Button(id="x", on_click=on_click),
)


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    router = AiogramRouterAdapter()
    window.register(router)
    router.add_handler(filter_widget_click, on_any_widget_click)

    dp.include_router(router)

    rendered = render_aiogram(
        window,
        RenderingContext(
            data={"name": "Tishka17"}
        ),
    )

    await bot.send_message(
        chat_id=1,
        text=rendered.text,
        reply_markup=rendered.reply_markup,
        disable_web_page_preview=True,
    )
    await dp.start_polling(bot)


asyncio.run(main())
