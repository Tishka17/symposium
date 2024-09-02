from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol

from symposium.core.finder import Finder


@dataclass(kw_only=True)
class RenderedItem:
    pass


@dataclass
class RenderingResult:
    items: list[RenderedItem]


@dataclass(frozen=True, kw_only=True)
class RenderingContext:
    data: dict = field(default_factory=dict)
    cache: dict = field(default_factory=dict)
    ui_root: Finder | None = None
    framework_data: Any = None
    chat_key: Any


class Renderer(Protocol):
    @abstractmethod
    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        raise NotImplementedError
