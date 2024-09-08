from typing import Any

from symposium.windows.stack import DialogStack, DialogContext
from symposium.windows.storage import StackStorage, ContextQuery, ChatT, SpecialIds


class MemoryStorage(StackStorage[Any]):
    def __init__(self):
        self.stacks: dict[Any, DialogStack] = {}
        self.contexts: dict[Any, DialogContext] = {}

    async def load_locked(self, query: ContextQuery[ChatT]) -> tuple[DialogStack, DialogContext | None]:
        if query.stack_id is SpecialIds.AUTO:
            if query.context_id is SpecialIds.AUTO:
                raise ValueError("Cannot load auto-auto")
            context_id = query.context_id
        else:
            stack = self.stacks.get((query.chat, query.stack_id), None)
            if stack is None:
                stack = DialogStack(_id=query.stack_id)

            if query.context_id is SpecialIds.AUTO:
                if not stack.intents:
                    return stack, None
                context_id = stack.intents[-1]
            else:
                context_id = query.context_id

        context: DialogContext = self.contexts.get((query.chat, context_id), None)
        if context is None:
            raise ValueError("Unknown context id")

        if query.stack_id is SpecialIds.AUTO:
            stack = self.stacks.get((query.chat, context.stack_id), None)
            if stack is None:
                raise ValueError("Stack not found")
        return stack, context

    async def save_context(self, chat: ChatT, context: DialogContext) -> None:
        self.contexts[(chat, context.id)] = context

    async def remove_context(self, chat: ChatT, context_id: str) -> None:
        del self.contexts[(chat, context_id)]

    async def save_stack(self, chat: ChatT, stack: DialogStack) -> None:
        self.stacks[chat, stack.id] = stack

    async def remove_stack(self, chat: ChatT, stack_id: str) -> None:
        del self.stacks[chat, stack_id]

    async def lock(self, query: ContextQuery[ChatT]):
        pass

    async def unlock(self, query: ContextQuery[ChatT]):
        pass
