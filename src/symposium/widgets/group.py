from dataclasses import replace
from typing import Any

from symposium.core import (
    RenderingContext,
    RenderingResult,
    Router,
)
from .base import BaseWidget, DataGetter


class Group(BaseWidget):
    def __init__(
        self,
        *widgets: BaseWidget,
        id: str | None = None,
        getter: DataGetter | None = None,
    ):
        super().__init__(id=id, getter=getter)
        self.widgets = widgets

    def register(self, router: Router) -> None:
        for widget in self.widgets:
            widget.register(router)

    def find(self, widget_id: str) -> Any:
        for widget in self.widgets:
            if found := widget.find(widget_id):
                return found
        return super().find(widget_id)

    async def _render(
        self,
        rendering_context: RenderingContext,
    ) -> RenderingResult:
        if rendering_context.ui_root is None:
            rendering_context = replace(rendering_context, ui_root=self)
        items = []
        for widget in self.widgets:
            widget_result = await widget.render(rendering_context)
            items.extend(widget_result.items)
        return RenderingResult(items)
