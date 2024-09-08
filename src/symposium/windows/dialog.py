from abc import abstractmethod
from typing import Protocol

from symposium.core import EventContext, RenderingResult
from symposium.events import Click
from symposium.render import Keyboard, KeyboardButton
from symposium.widgets.base import BaseWidget
from symposium.windows.widget_context import (
    StatefulContext,
    StatefulEventContext,
    StatefulRenderingContext,
)
from symposium.windows.state import State

INTENT_ID_SEP = "\x1d"


class Adapter(Protocol):
    @abstractmethod
    async def show(
        self,
        rendering_result: RenderingResult,
        rendering_context: StatefulRenderingContext,
    ) -> None:
        raise NotImplementedError


class IntentHandler:
    def __init__(
        self,
        windows: dict[State, BaseWidget],
        adapter: Adapter,
    ):
        self.windows = windows
        self.adapter = adapter

    def current_window(self, context: StatefulContext) -> BaseWidget:
        return self.windows[context.transition_manager.get_current_state()]

    async def render(
        self,
        rendering_context: StatefulRenderingContext,
    ) -> RenderingResult:
        window = self.current_window(rendering_context)
        result = await window.render(rendering_context)
        return self._add_intent_id(result, rendering_context)

    def _add_intent_id(
        self, result: RenderingResult, context: StatefulContext
    ) -> RenderingResult:
        new_items = []
        for item in result.items:
            if isinstance(item, Keyboard):
                item = Keyboard(
                    buttons=[
                        [
                            KeyboardButton(
                                data=f"{context.intent_id}{INTENT_ID_SEP}{button.data}",
                                text=button.text,
                            )
                            if isinstance(button, KeyboardButton)
                            else button
                            for button in row
                        ]
                        for row in item.buttons
                    ]
                )
            new_items.append(item)
        return RenderingResult(items=new_items)

    def filter(self, context: EventContext) -> bool:
        if not isinstance(context.event, Click):
            return False
        if INTENT_ID_SEP not in context.event.data:
            return False
        return True

    async def handle(self, context: EventContext):
        if not isinstance(context.event, Click):
            return
        intent_id, data = context.event.data.split(INTENT_ID_SEP)

        # TODO: load context from DB
        state = intent_id
        ui_root = self.windows[state]
        stateful_context = StatefulEventContext(
            ui_root=ui_root,
            widget_data={},
            event=Click(
                data=data,
                parent_event=context.event,
            ),
            chat_key=context.chat_key,
            intent_id=intent_id,
            framework_data=context.framework_data,
            router=context.router,
            stack_id="",  # TODO: rom intent
            transition_manager=None,  # TODO
        )
        handler = context.router.prepare_handlers(stateful_context)
        await handler.handle(stateful_context)
        # TODO where to refresh?
        ui_root = self.windows[state]
        rendering_context = StatefulRenderingContext(
            ui_root=ui_root,
            widget_data={},
            intent_id=intent_id,
            chat_key=context.chat_key,
            framework_data=context.framework_data,
            stack_id="",  # TODO: rom intent
            transition_manager=None,  # TODO
        )
        result = await ui_root.render(rendering_context)
        await self.adapter.show(result, rendering_context)
