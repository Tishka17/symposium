from dataclasses import dataclass
from typing import Any

from aiogram import Bot
from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    MessageEntity,
    TelegramObject,
)

from symposium.core import Finder, Renderer, RenderingContext, RenderingResult
from symposium.events import Click, SymposiumEvent
from symposium.handle import EventContext, HandlerHolder, Router
from symposium.render import Keyboard, KeyboardButton, Text
from symposium.router import SimpleRouter


@dataclass
class AiogramRenderingResult:
    text: str
    entities: list[MessageEntity] | None
    reply_markup: InlineKeyboardMarkup


def _to_inline_button(button: KeyboardButton) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=button.text,
        callback_data=button.data,
    )


def _append_keyboard(item: Keyboard, target: AiogramRenderingResult) -> None:
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
            target.reply_markup.inline_keyboard.append(new_row)


def _append_text(item: Text, target: AiogramRenderingResult) -> None:
    target.text += item.text


def to_aiogram(data: RenderingResult) -> AiogramRenderingResult:
    res = AiogramRenderingResult(
        text="",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
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


async def render_aiogram(
    widget: Renderer,
    context: RenderingContext | None = None,
) -> AiogramRenderingResult:
    if context is None:
        context = RenderingContext()
    return to_aiogram(await widget.render(context))


def aiogram_event(context: EventContext) -> TelegramObject | None:
    event = context.event
    while True:
        if isinstance(event, TelegramObject):
            return event
        if not isinstance(event, SymposiumEvent):
            return None
        event = event.parent_event


class AiogramRouterAdapter(AiogramRouter):
    def __init__(
        self,
        router: Router,
        ui_root: Finder,
    ):
        super().__init__()
        self.router = router
        self.ui_root = ui_root

    def resolve_used_update_types(
        self,
        skip_events: set[str] | None = None,
    ) -> list[str]:
        return ["callback"]

    async def propagate_event(
        self,
        update_type: str,
        event: TelegramObject,
        **kwargs: Any,
    ) -> Any:
        if not isinstance(event, CallbackQuery):
            return UNHANDLED

        click = EventContext(
            event=Click(
                data=event.data,
                parent_event=event,
            ),
            router=self.router,
            ui_root=self.ui_root,
        )
        handler = self.router.prepare_handlers(click)
        if not handler:
            return UNHANDLED
        await handler.handle(click)


def register_handler(widget: HandlerHolder, router: AiogramRouter) -> Router:
    symposium_router = SimpleRouter()
    widget.register(symposium_router)

    adapter = AiogramRouterAdapter(symposium_router, widget)
    router.include_router(adapter)
    return symposium_router


class MessageManager:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(
        self,
        chat_id: int,
        data: AiogramRenderingResult,
        **kwargs,
    ) -> Message:
        return await self.bot.send_message(
            chat_id=chat_id,
            text=data.text,
            reply_markup=data.reply_markup,
            **kwargs,
        )
