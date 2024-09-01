from abc import abstractmethod
from typing import Any, Protocol


class Finder(Protocol):
    @abstractmethod
    def find(self, widget_id: str) -> Any:
        raise NotImplementedError
