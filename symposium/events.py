from dataclasses import dataclass
from typing import Any


@dataclass
class SimposiumEvent:
    parent_event: Any


@dataclass
class Click(SimposiumEvent):
    data: str


@dataclass
class WidgetClick(SimposiumEvent):
    data: Any
    source: Any
