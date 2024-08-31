import asyncio
import os

from aiogram import Bot, Dispatcher

from symposium.aiogram import to_inline_keyboard, AiogramRouterAdapter, to_text
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
    window.register(router.router)

    dp.include_router(router)

    rendered = window.render(RenderingContext(
        data={"name": "Tishka17"}
    ))

    await bot.send_message(
        chat_id=1,
        text=to_text(rendered),
        reply_markup=to_inline_keyboard(rendered),
        disable_web_page_preview=True,
    )
    await dp.start_polling(bot)


asyncio.run(main())
