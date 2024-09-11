from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

from symposium.core.context import BaseContext


@dataclass(kw_only=True)
class RenderedItem:
    pass


@dataclass
class RenderingResult:
    items: list[RenderedItem]


@dataclass(frozen=True, kw_only=True)
class RenderingContext(BaseContext):
    data: dict = field(default_factory=dict)
    cache: dict = field(default_factory=dict)


class Renderer(Protocol):
    @abstractmethod
    async def render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        raise NotImplementedError
