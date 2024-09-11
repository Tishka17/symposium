import uuid
from typing import Any

from symposium.core import SymposiumEvent, Router
from symposium.windows.protocols.storage import StackStorage
from symposium.windows.protocols.transition_manager import TransitionManager
from symposium.windows.registry import DialogRegistry
from symposium.windows.stack import DialogContext, DialogStack
from symposium.windows.state import State
from symposium.windows.widget_context import StatefulEventContext, StatefulRenderingContext


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


    def event_context(self, event: SymposiumEvent, router: Router, framework_data: Any) -> StatefulEventContext:
        return StatefulEventContext(
            event=event,
            context=self._context,
            stack=self._stack,
            transition_manager=self,
            router=router,
            ui_root=self,
            framework_data=framework_data,
            chat_key=self._chat,
        )

    def rendering_context(self, framework_data: Any) -> StatefulRenderingContext:
        return StatefulRenderingContext(
            context=self._context,
            stack=self._stack,
            transition_manager=self,
            ui_root=self,
            framework_data=framework_data,
            chat_key=self._chat,
        )

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
