from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol


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
    entities: list[Any] | None


@dataclass
class RenderingResult:
    items: list[RenderedItem]


@dataclass
class RenderingContext:
    data: dict = field(default_factory=dict)
    cache: dict = field(default_factory=dict)


class Renderer(Protocol):
    @abstractmethod
    def render(self, rendering_context: RenderingContext) -> RenderingResult:
        raise NotImplementedError
