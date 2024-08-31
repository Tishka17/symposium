from dataclasses import dataclass
from typing import Any


@dataclass
class Click:
    data: str
    parent_event: Any
