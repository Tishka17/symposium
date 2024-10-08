from symposium.core import Filter, Handler
from symposium.core.router import BaseEventContext, RouteRegistry
from symposium.widgets.base import BaseWidget, DataGetter
from symposium.widgets.group import Group
from symposium.windows.state import State
from symposium.windows.widget_context import StatefulEventContext


class StateFilter(Filter):
    def __init__(self, state: State, filter: Filter):
        self.state = state
        self.filter = filter

    def __call__(self, context: BaseEventContext) -> bool:
        if not isinstance(context, StatefulEventContext):
            return False
        if context.context is None:
            return False
        if context.context.state != self.state:
            return False
        return self.filter(context)


class RouterWrapper(RouteRegistry):
    def __init__(self, router: RouteRegistry, state: State):
        self.router = router
        self.state = state

    def add_handler(self, filter: Filter, handler: Handler) -> None:
        self.router.add_handler(StateFilter(self.state, filter), handler)


class Window(Group):
    def __init__(
        self,
        *widgets: BaseWidget,
        id: str | None = None,
        getter: DataGetter | None = None,
        state: State | None = None,
    ):
        super().__init__(*widgets, id=id, getter=getter)
        self.state = state

    def register(self, router: RouteRegistry) -> None:
        wrapper = RouterWrapper(router, self.state)
        super().register(wrapper)
