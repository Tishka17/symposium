from dataclasses import dataclass

from symposium.core import EventContext, RenderingContext
from .stack import DialogStack, DialogContext
from .storage import ChatT
from .transition_manager import TransitionManager


@dataclass(frozen=True, kw_only=True)
class StatefulContext:
    stack: DialogStack
    context: DialogContext
    transition_manager: TransitionManager


@dataclass(frozen=True, kw_only=True)
class StatefulRenderingContext(RenderingContext, StatefulContext):
    pass


@dataclass(frozen=True, kw_only=True)
class StatefulEventContext(EventContext, StatefulContext):
    pass
