from dataclasses import dataclass
from typing import Any

from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    MessageEntity,
)

from symposium.core import Finder, Renderer, RenderingContext, RenderingResult
from symposium.events import Click, SymposiumEvent
from symposium.handle import EventContext, Router
from symposium.render import Keyboard, KeyboardButton, Text
from symposium.router import SimpleRouter
from symposium.widgets.base import BaseWidget


@dataclass(frozen=True)
class TelebotChatKey:
    chat_id: int


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
                raise ValueError(f"Unexpected button: {button}")
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
                raise ValueError(f"Unexpected item: {item}")
    return res


async def render_telebot(
    widget: Renderer,
    context: RenderingContext | None = None,
) -> TelebotRenderingResult:
    if context is None:
        context = RenderingContext()
    return to_telebot(await widget.render(context))


def telebot_event(context: EventContext) -> CallbackQuery | None:
    event = context.event
    while True:
        if isinstance(event, CallbackQuery):
            return event
        if not isinstance(event, SymposiumEvent):
            return None
        event = event.parent_event


class TelebotAdapter:
    def __init__(
        self,
        router: Router,
        ui_root: Finder,
    ):
        super().__init__()
        self.router = router
        self.ui_root = ui_root

    def filter_callback(
        self,
        event: CallbackQuery,
    ):
        return bool(
            self.router.prepare_handlers(
                EventContext(
                    event=Click(
                        data=event.data,
                        parent_event=event,
                    ),
                    router=self.router,
                    ui_root=self.ui_root,
                    chat_key=TelebotChatKey(chat_id=event.message.chat.id),
                ),
            ),
        )

    async def handle_callback(
        self,
        event: CallbackQuery,
        **kwargs: Any,
    ) -> Any:
        click = EventContext(
            event=Click(
                data=event.data,
                parent_event=event,
            ),
            router=self.router,
            ui_root=self.ui_root,
            framework_data=kwargs,
            chat_key=TelebotChatKey(chat_id=event.message.chat.id),
        )
        handler = self.router.prepare_handlers(click)
        await handler.handle(click)


def register_handler(widget: BaseWidget, bot: AsyncTeleBot) -> Router:
    symposium_router = SimpleRouter()
    widget.register(symposium_router)

    adapter = TelebotAdapter(symposium_router, widget)
    bot.register_callback_query_handler(
        adapter.handle_callback,
        adapter.filter_callback,
    )
    return symposium_router


class MessageManager:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    async def send(
        self,
        chat_id: int,
        data: TelebotRenderingResult,
        **kwargs,
    ) -> Message:
        return await self.bot.send_message(
            chat_id=chat_id,
            text=data.text,
            reply_markup=data.reply_markup,
            **kwargs,
        )
