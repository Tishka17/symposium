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

from symposium.core import (
    EventContext,
    Finder,
    Renderer,
    RenderingContext,
    RenderingResult,
    Router,
)
from symposium.events import Click, SymposiumEvent
from symposium.handle import BaseEventContext, RouteRegistry
from symposium.integrations.telegram_base import ChatContext
from symposium.render import Keyboard, KeyboardButton, Text
from symposium.router import SimpleRouter
from symposium.widgets.base import BaseWidget


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
        context = RenderingContext(
            ui_root=widget,
            chat_key=None,
        )
    return to_telebot(await widget.render(context))


def telebot_event(context: BaseEventContext) -> CallbackQuery | None:
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
        chat_key = ChatContext(
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            thread_id=event.message.message_thread_id,
            business_connection_id=event.message.business_connection_id,
        )
        res = bool(
            self.router.prepare_handlers(
                EventContext(
                    event=Click(
                        data=event.data,
                        parent_event=event,
                    ),
                    router=self.router,
                    ui_root=self.ui_root,
                    chat_key=chat_key,
                ),
            ),
        )
        print("FILTERED", res)
        return res

    async def handle_callback(
        self,
        event: CallbackQuery,
        **kwargs: Any,
    ) -> Any:
        print("FILTER")
        chat_key = ChatContext(
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            thread_id=event.message.message_thread_id,
            business_connection_id=event.message.business_connection_id,
        )
        click = EventContext(
            event=Click(
                data=event.data,
                parent_event=event,
            ),
            router=self.router,
            ui_root=self.ui_root,
            framework_data=kwargs,
            chat_key=chat_key,
        )
        await self.router.handle(click)


def register_handler(widget: BaseWidget, bot: AsyncTeleBot) -> RouteRegistry:
    symposium_router = SimpleRouter()
    widget.register(symposium_router)

    adapter = TelebotAdapter(symposium_router, widget)
    bot.register_callback_query_handler(
        adapter.handle_callback,
        adapter.filter_callback,
        pass_bot=True,
    )
    return symposium_router


class MessageManager:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    async def convert(self, result: RenderingResult) -> TelebotRenderingResult:
        return to_telebot(result)

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
