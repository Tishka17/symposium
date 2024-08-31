import asyncio
import os

from aiogram import Bot, Dispatcher

from symposium.aiogram import AiogramRouterAdapter, render_aiogram, aiogram_event
from symposium.handle import EventContext
from symposium.render import RenderingContext
from symposium.widgets import Button, Group, Format


async def on_click(context: EventContext):
    print("Click detected")
    callback = aiogram_event(context)
    await callback.answer("Click detected")


window = Group(
    Format("Hello, {name}"),
    Button(id="x", on_click=on_click),
)


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    router = AiogramRouterAdapter()
    window.register(router)

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
