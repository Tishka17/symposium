from abc import abstractmethod
from typing import Protocol

from symposium.core import RenderingContext, RenderingResult


class WindowSender(Protocol):
    @abstractmethod
    async def send(
        self, data: RenderingResult, context: RenderingContext,
    ) -> None:
        raise NotImplementedError
