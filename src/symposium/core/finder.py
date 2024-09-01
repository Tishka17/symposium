from abc import abstractmethod
from typing import Protocol, Any


class Finder(Protocol):
    @abstractmethod
    def find(self, widget_id: str) -> Any:
        raise NotImplementedError
