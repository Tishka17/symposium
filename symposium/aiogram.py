from typing import Any

from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, TelegramObject, CallbackQuery

from symposium.events import Click
from symposium.handle import EventContext
from symposium.render import KeyboardButton
from symposium.render import RenderingResult, Keyboard
from symposium.router import SimpleRouter


def _to_inline_button(button: KeyboardButton) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=button.text,
        callback_data=button.data,
    )


def to_inline_keyboard(data: RenderingResult) -> None | InlineKeyboardMarkup:
    new_buttons: list[list[InlineKeyboardButton]] = []
    for item in data.items:
        if not isinstance(item, Keyboard):
            continue
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
                new_buttons.append(new_row)
    if not new_buttons:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=new_buttons,
    )


class AiogramRouterAdapter(AiogramRouter):
    def __init__(self):
        super().__init__()
        self.router = SimpleRouter()

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
        handler.handle(click)
