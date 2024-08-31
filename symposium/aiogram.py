from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router as AiogramRouter

from symposium.handle import Router
from symposium.render import KeyboardButton
from symposium.render import RenderingResult, Keyboard


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
        self.router = Router()

