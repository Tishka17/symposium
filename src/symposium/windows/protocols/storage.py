from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Generic, Protocol, TypeVar

from symposium.windows.stack import DialogContext, DialogStack


class SpecialIds(Enum):
    AUTO = "AUTO"


ChatT = TypeVar("ChatT")


@dataclass
class ContextQuery(Generic[ChatT]):
    chat: ChatT
    stack_id: str | SpecialIds
    context_id: str | SpecialIds


class StackStorage(Protocol[ChatT]):
    @abstractmethod
    async def load_locked(
        self, query: ContextQuery[ChatT],
    ) -> tuple[DialogStack, DialogContext | None]:
        raise NotImplementedError

    @abstractmethod
    async def save_context(self, chat: ChatT, context: DialogContext) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_context(self, chat: ChatT, context_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_stack(self, chat: ChatT, stack: DialogStack) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_stack(self, chat: ChatT, stack_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def unlock(self, query: ContextQuery[ChatT]):
        raise NotImplementedError
