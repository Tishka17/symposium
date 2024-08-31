import asyncio
import os

from aiogram import Bot, Dispatcher

from symposium.aiogram import AiogramRouterAdapter, render_aiogram
from symposium.render import RenderingContext
from symposium.widgets import Button, Group, Format

window = Group(
    Format("Hello, {name}"),
    Button(id="x"),
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
