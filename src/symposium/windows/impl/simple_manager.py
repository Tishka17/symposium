from typing import Any

from symposium.core import Router, SymposiumEvent
from symposium.windows.impl.transitions import TransitionManager
from symposium.windows.protocols.dialog_manager import DialogManager
from symposium.windows.registry import DialogRegistry
from symposium.windows.state import State
from symposium.windows.widget_context import (
    StatefulEventContext,
    StatefulRenderingContext,
)


class SimpleDialogManager(DialogManager):
    def __init__(
        self,
        chat: Any,
        registry: DialogRegistry,
        transition_manager: TransitionManager,
    ):
        self._chat = chat
        self._registry = registry
        self._transition_manager = transition_manager

    def event_context(
        self,
        event: SymposiumEvent,
        router: Router,
        framework_data: Any,
    ) -> StatefulEventContext:
        return StatefulEventContext(
            event=event,
            context=self._transition_manager.get_current_context(),
            stack=self._transition_manager.get_current_stack(),
            dialog_manager=self,
            router=router,
            ui_root=self,
            framework_data=framework_data,
            chat_key=self._chat,
        )

    def rendering_context(
        self,
        framework_data: Any,
    ) -> StatefulRenderingContext:
        return StatefulRenderingContext(
            context=self._transition_manager.get_current_context(),
            stack=self._transition_manager.get_current_stack(),
            dialog_manager=self,
            ui_root=self,
            framework_data=framework_data,
            chat_key=self._chat,
        )

    async def _show(self):
        pass

    async def close(self):
        await self._transition_manager.close()
        await self._show()

    async def start(self, state: State) -> None:
        await self._transition_manager.start(state)
        await self._show()

    async def switch(self, state: State) -> None:
        await self._transition_manager.switch(state)
        await self._show()

    def get_current_state(self) -> State:
        return self._transition_manager.get_current_state()

    def find(self, widget_id: str) -> Any:
        window = self._registry.find_window(self.get_current_state())
        return window.find(widget_id)
