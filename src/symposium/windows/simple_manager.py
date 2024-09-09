import uuid
from typing import Any

from symposium.windows.registry import DialogRegistry
from symposium.windows.stack import DialogContext, DialogStack
from symposium.windows.state import State
from symposium.windows.storage import StackStorage
from symposium.windows.transition_manager import TransitionManager


class SimpleTransitionManager(TransitionManager):
    def __init__(
            self,
            chat: Any,
            registry: DialogRegistry,
            context: DialogContext,
            stack: DialogStack,
            storage: StackStorage,
    ):
        self._chat = chat
        self._registry = registry
        self._context = context
        self._stack = stack
        self._storage = storage

    async def start(self, state: State) -> None:
        context = DialogContext(
            _stack_id=self._stack.id,
            _intent_id=str(uuid.uuid4()),  # FIXME
            state=state,
            start_state=state,
        )
        self._stack.intents.append(context.id)
        self._context = context

        await self._storage.save_context(self._chat, self._context)
        await self._storage.save_stack(self._chat, self._stack)

    async def switch(self, state: State) -> None:
        self._context.state = state
        await self._storage.save_context(self._chat, self._context)

    def get_current_state(self) -> State:
        return self._context.state

    def find(self, widget_id: str) -> Any:
        window = self._registry.find_window(self.get_current_state())
        return window.find(widget_id)
