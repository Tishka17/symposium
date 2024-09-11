from dataclasses import dataclass

from symposium.core import BaseContext, EventContext, RenderingContext
from .protocols.transition_manager import TransitionManager
from .stack import DialogContext, DialogStack


@dataclass(frozen=True, kw_only=True)
class StatefulContext(BaseContext):
    stack: DialogStack
    context: DialogContext
    transition_manager: TransitionManager


@dataclass(frozen=True, kw_only=True)
class StatefulRenderingContext(RenderingContext, StatefulContext):
    pass


@dataclass(frozen=True, kw_only=True)
class StatefulEventContext(EventContext, StatefulContext):
    pass
