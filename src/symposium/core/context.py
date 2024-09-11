from dataclasses import dataclass
from typing import Any

from .finder import Finder


@dataclass(frozen=True, kw_only=True)
class BaseContext:
    ui_root: Finder | None
    chat_key: Any
    framework_data: Any = None
