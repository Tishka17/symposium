from dataclasses import dataclass
from typing import Any

from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, MessageEntity,
    Message,
)

from symposium.events import Click, SimposiumEvent
from symposium.handle import EventContext, Router, HandlerHolder
from symposium.render import KeyboardButton, Text, Renderer, RenderingContext
from symposium.render import RenderingResult, Keyboard
from symposium.router import SimpleRouter


@dataclass
class TelebotRenderingResult:
    text: str
    entities: list[MessageEntity] | None
    reply_markup: InlineKeyboardMarkup


def _to_inline_button(button: KeyboardButton) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=button.text,
        callback_data=button.data,
    )


def _append_keyboard(item: Keyboard, target: TelebotRenderingResult) -> None:
    for row in item.buttons:
        new_row = []
        for button in row:
            if isinstance(button, InlineKeyboardButton):
                new_row.append(button)
            elif isinstance(button, KeyboardButton):
                new_row.append(_to_inline_button(button))
            else:
                raise ValueError(f'Unexpected button: {button}')
        if new_row:
            target.reply_markup.keyboard.append(new_row)


def _append_text(item: Text, target: TelebotRenderingResult) -> None:
    target.text += item.text


def to_telebot(data: RenderingResult) -> TelebotRenderingResult:
    res = TelebotRenderingResult(
        text="",
        reply_markup=InlineKeyboardMarkup(keyboard=[]),
        entities=[],
    )
    for item in data.items:
        match item:
            case Text() as text:
                _append_text(text, res)
            case Keyboard() as keyboard:
                _append_keyboard(keyboard, res)
            case _:
                raise ValueError(f'Unexpected item: {item}')
    return res


def render_telebot(widget: Renderer, context: RenderingContext) -> TelebotRenderingResult:
    return to_telebot(widget.render(context))


def telebot_event(context: EventContext) -> CallbackQuery | None:
    event = context.event
    while True:
        if isinstance(event, CallbackQuery):
            return event
        if not isinstance(event, SimposiumEvent):
            return None
        event = event.parent_event


class TelebotAdapter:

    def __init__(self, router: Router):
        super().__init__()
        self.router = router

    def filter_callback(self, event: CallbackQuery, ):
        return bool(
            self.router.prepare_handlers(EventContext(
                event=Click(
                    data=event.data,
                    parent_event=event,
                ),
                router=self.router,
            ))
        )

    async def handle_callback(self, event: CallbackQuery, **kwargs: Any) -> Any:
        click = EventContext(
            event=Click(
                data=event.data,
                parent_event=event,
            ),
            router=self.router,
        )
        handler = self.router.prepare_handlers(click)
        await handler.handle(click)


def register_handler(widget: HandlerHolder, bot: AsyncTeleBot) -> Router:
    symposium_router = SimpleRouter()
    widget.register(symposium_router)

    adapter = TelebotAdapter(symposium_router)
    bot.register_callback_query_handler(
        adapter.handle_callback,
        adapter.filter_callback
    )
    return symposium_router


class MessageManager:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    async def send(
            self, chat_id: int, data: TelebotRenderingResult,
            **kwargs,
    ) -> Message:
        return await self.bot.send_message(
            chat_id=chat_id,
            text=data.text,
            reply_markup=data.reply_markup,
            **kwargs,
        )
