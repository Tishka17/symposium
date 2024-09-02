from abc import abstractmethod
from typing import Protocol

from symposium.windows.state import State


class TransitionManager(Protocol):
    @abstractmethod
    def get_current_state(self) -> State:
        raise NotImplementedError
