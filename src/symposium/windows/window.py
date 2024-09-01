from collections.abc import Awaitable, Callable
from dataclasses import replace

from symposium.core import RenderingContext, RenderingResult
from symposium.widgets import Group

DataGetter = Callable[[RenderingContext], Awaitable[dict]]


class GetterGroup(Group):
    def __init__(self, *widgets, getter: DataGetter):
        super().__init__(*widgets)
        self.getter = getter

    async def render(self, context: RenderingContext) -> RenderingResult:
        data = await self.getter(context)
        return await super().render(replace(context, data=context.data | data))
