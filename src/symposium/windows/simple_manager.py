from typing import Any

from symposium.windows.registry import DialogRegistry
from symposium.windows.stack import DialogContext, DialogStack
from symposium.windows.state import State
from symposium.windows.transition_manager import TransitionManager


class SimpleTransitionManager(TransitionManager):
    def __init__(
            self,
            registry: DialogRegistry,
            context: DialogContext,
            stack: DialogStack,
    ):
        self._registry = registry
        self._context = context
        self._stack = stack

    def get_current_state(self) -> State:
        return self._context.state

    def find(self, widget_id: str) -> Any:
        window = self._registry.find_window(self.get_current_state())
        return window.find(widget_id)
