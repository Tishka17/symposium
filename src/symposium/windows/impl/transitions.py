from typing import Any

from symposium.windows.protocols.storage import StackStorage
from symposium.windows.stack import DialogContext, DialogStack
from symposium.windows.state import State


class TransitionManager:
    def __init__(
        self,
        chat: Any,
        context: DialogContext,
        stack: DialogStack,
        storage: StackStorage,
    ):
        self._chat = chat
        self._context = context
        self._stack = stack
        self._storage = storage

    async def close(self):
        intent_id = self._stack.intents.pop()
        await self._storage.remove_context(self._chat, intent_id)
        await self._storage.save_stack(self._chat, self._stack)

    async def start(self, state: State) -> None:
        new_id = self._stack.new_intent_number()
        context = DialogContext(
            _stack_id=self._stack.id,
            _intent_id=str(new_id),
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

    def get_current_context(self) -> DialogContext:
        return self._context

    def get_current_stack(self) -> DialogStack:
        return self._stack
