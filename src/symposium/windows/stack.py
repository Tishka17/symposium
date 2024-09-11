from dataclasses import dataclass, field
from typing import Any

from .state import State


@dataclass(unsafe_hash=True)
class DialogStack:
    _id: str = field(compare=True)
    intents: list[str] = field(compare=False, default_factory=list)
    access_settings: dict[str, Any] = field(
        compare=False,
        default_factory=dict,
    )

    @property
    def id(self):
        return self._id


@dataclass(unsafe_hash=True)
class DialogContext:
    _intent_id: str = field(compare=True)
    _stack_id: str = field(compare=True)
    state: State = field(compare=False)
    start_state: State = field(compare=False)
    dialog_data: dict[str, Any] = field(compare=False, default_factory=dict)
    widget_data: dict[str, Any] = field(compare=False, default_factory=dict)
    caller_data: dict[str, Any] = field(compare=False, default_factory=dict)
    access_settings: dict[str, Any] = field(
        compare=False,
        default_factory=dict,
    )

    @property
    def id(self) -> str:
        return self._intent_id

    @property
    def stack_id(self) -> str:
        return self._stack_id
