from dataclasses import dataclass, field
from typing import Any

from symposium.core import EventContext, RenderingContext
from .transition_manager import TransitionManager


@dataclass(frozen=True, kw_only=True)
class StatefulContext:
    widget_data: dict[str, Any] = field(default_factory=dict)
    dialog_data: dict[str, Any] = field(default_factory=dict)
    transition_manager: TransitionManager
    intent_id: str
    stack_id: str


@dataclass(frozen=True, kw_only=True)
class StatefulRenderingContext(RenderingContext, StatefulContext):
    pass


@dataclass(frozen=True, kw_only=True)
class StatefulEventContext(EventContext, StatefulContext):
    pass
