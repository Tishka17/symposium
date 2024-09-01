from dataclasses import dataclass
from typing import Any

from symposium.core import SymposiumEvent


@dataclass
class Click(SymposiumEvent):
    data: str


@dataclass
class WidgetClick(SymposiumEvent):
    data: Any
    source: Any
