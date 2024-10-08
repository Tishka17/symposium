from abc import abstractmethod
from typing import Any, Protocol

from symposium.core import Finder, Router, SymposiumEvent
from symposium.windows.state import State
from symposium.windows.widget_context import (
    StatefulEventContext,
    StatefulRenderingContext,
)


class DialogManager(Finder, Protocol):
    @abstractmethod
    def event_context(
        self,
        event: SymposiumEvent,
        router: Router,
        framework_data: Any,
    ) -> StatefulEventContext:
        raise NotImplementedError

    @abstractmethod
    def rendering_context(
        self,
        framework_data: Any,
    ) -> StatefulRenderingContext:
        raise NotImplementedError

    @abstractmethod
    def get_current_state(self) -> State:
        raise NotImplementedError

    @abstractmethod
    async def start(self, state: State) -> None:
        raise NotImplementedError

    @abstractmethod
    async def switch(self, state: State) -> None:
        raise NotImplementedError
