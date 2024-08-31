from dataclasses import dataclass
from typing import Any

from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, MessageEntity, TelegramObject

from symposium.events import Click
from symposium.handle import EventContext, Router, Filter, Handler
from symposium.render import KeyboardButton, Text, Renderer, RenderingContext
from symposium.render import RenderingResult, Keyboard
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
                raise ValueError(f'Unexpected button: {button}')
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
                raise ValueError(f'Unexpected item: {item}')
    return res

def render_aiogram(widget: Renderer, context: RenderingContext) -> AiogramRenderingResult:
    return to_aiogram(widget.render(context))


class AiogramRouterAdapter(AiogramRouter, Router):

    def __init__(self):
        super().__init__()
        self.router = SimpleRouter()

    def add_handler(self, filter: Filter, handler: Handler) -> None:
        self.router.add_handler(filter, handler)

    def resolve_used_update_types(self, skip_events: set[str] | None = None) -> list[str]:
        return ["callback"]

    async def propagate_event(self, update_type: str, event: TelegramObject, **kwargs: Any) -> Any:
        if not isinstance(event, CallbackQuery):
            return UNHANDLED

        click = EventContext(
            event=Click(
                data=event.data,
                parent_event=event,
            )
        )
        handler = self.router.prepare_handlers(click)
        if not handler:
            return UNHANDLED
        await handler.handle(click)
