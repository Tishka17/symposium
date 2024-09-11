from dataclasses import dataclass
from typing import Any

from symposium.core import RenderingResult


@dataclass(kw_only=True)
class RenderedItem:
    pass


@dataclass
class KeyboardButton:
    text: str
    data: str


@dataclass
class Keyboard(RenderedItem):
    buttons: list[list[Any]]


@dataclass
class Text(RenderedItem):
    text: str


def extract_text(rendered: RenderingResult):
    return "".join(
        item.text for item in rendered.items if isinstance(item, Text)
    )
