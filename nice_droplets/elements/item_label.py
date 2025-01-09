from typing import Optional, TypedDict

from nicegui import ui
from typing_extensions import NotRequired
from nicegui.elements.mixins.text_element import TextElement


class ItemLabelKwargs(TypedDict):
    caption: NotRequired[bool]
    header: NotRequired[bool]
    overline: NotRequired[bool]
    lines: NotRequired[Optional[int]]


class ItemLabel(TextElement):
    _ITEM_LABEL_PROPS = {
        'caption': 'caption',
        'header': 'header',
        'overline': 'overline',
        'lines': 'lines'
    }

    def __init__(self, text: str, **kwargs: ItemLabelKwargs) -> None:
        """List Item Label

        Creates an item label based on Quasar's `QItemLabel <https://quasar.dev/vue-components/list-and-list-items#qitemlabel-api>`_ component.

        :param text: text to be displayed
        :param kwargs: Additional keyword arguments:
            - caption (bool): creates a caption label (smaller, lighter text)
            - header (bool): creates a header label (bolder, larger text)
            - overline (bool): creates an overline label (uppercase, small text)
            - lines (Optional[int]): number of lines to show before truncating (only works with caption)
        """
        super().__init__(tag='q-item-label', text=text)

        for py_prop, vue_prop in self._ITEM_LABEL_PROPS.items():
            if py_prop in kwargs:
                self._props[vue_prop] = kwargs[py_prop]
