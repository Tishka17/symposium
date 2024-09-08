from abc import abstractmethod
from typing import Protocol, Any

from symposium.core import Finder
from symposium.windows.state import State


class TransitionManager(Finder, Protocol):
    @abstractmethod
    def get_current_state(self) -> State:
        raise NotImplementedError