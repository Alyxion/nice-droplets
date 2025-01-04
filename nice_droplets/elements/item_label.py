from typing import Optional

from nicegui import ui
from nicegui.elements.mixins.text_element import TextElement
from pathlib import Path


class ItemLabel(TextElement, component=str(Path(__file__).parent / 'item_label.js')):
    def __init__(
        self,
        text: str = '',
        *,
        caption: bool = False,
        header: bool = False,
        overline: bool = False,
        lines: Optional[int] = None
    ) -> None:
        """Create a Quasar item label element.

        Args:
            text: The text content of the label
            caption: If True, creates a caption label (smaller, lighter text)
            header: If True, creates a header label (bolder, larger text)
            overline: If True, creates an overline label (uppercase, small text)
            lines: Number of lines to show before truncating (only works with caption)
        """
        super().__init__(text=text)
        
        if caption:
            self.classes('q-item-label--caption')
        elif header:
            self.classes('q-item-label--header')
        elif overline:
            self.classes('q-item-label--overline')
            
        if lines is not None:
            self._props['lines'] = lines
