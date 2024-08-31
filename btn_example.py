import asyncio
import os

from aiogram import Bot, Dispatcher

from symposium.aiogram import to_inline_keyboard, AiogramRouterAdapter
from symposium.render import RenderingContext
from symposium.widgets import Button

btn = Button(id="x")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    router = AiogramRouterAdapter()
    btn.register(router.router)

    dp.include_router(router)

    rendered = btn.render(RenderingContext())

    await bot.send_message(
        chat_id=1,
        text="hij",
        reply_markup=to_inline_keyboard(rendered),
        disable_web_page_preview=True,
    )
    await dp.start_polling(bot)



asyncio.run(main())
