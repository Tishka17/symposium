from symposium.core import (
    RenderingContext,
)
from symposium.render import Text
from .base import BaseWidget


class Format(BaseWidget):
    def __init__(self, text: str, id: str | None = None):
        super().__init__(id)
        self.text = text

    async def _render_single(
        self,
        rendering_context: RenderingContext,
    ) -> Text:
        rendered_text = self.text.format_map(
            rendering_context.data,
        )
        return Text(text=rendered_text)
