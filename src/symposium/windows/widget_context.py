from dataclasses import dataclass
from typing import Any

from symposium.core import BaseContext, EventContext, RenderingContext
from .stack import DialogContext, DialogStack


@dataclass(frozen=True, kw_only=True)
class StatefulContext(BaseContext):
    stack: DialogStack
    context: DialogContext
    transition_manager: Any


@dataclass(frozen=True, kw_only=True)
class StatefulRenderingContext(RenderingContext, StatefulContext):
    pass


@dataclass(frozen=True, kw_only=True)
class StatefulEventContext(EventContext, StatefulContext):
    pass
