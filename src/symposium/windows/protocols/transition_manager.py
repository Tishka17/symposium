from abc import abstractmethod
from typing import Protocol

from symposium.core import Finder
from symposium.windows.state import State


class TransitionManager(Finder, Protocol):
    @abstractmethod
    def get_current_state(self) -> State:
        raise NotImplementedError

    @abstractmethod
    async def start(self, state: State) -> None:
        raise NotImplementedError

    @abstractmethod
    async def switch(self, state: State) -> None:
        raise NotImplementedError
