from typing import Optional, TypedDict, Self

from nicegui import ui
from typing_extensions import NotRequired
from nicegui.elements.mixins.text_element import TextElement


class ItemSectionKwargs(TypedDict):
    avatar: NotRequired[bool]
    thumbnail: NotRequired[bool]
    side: NotRequired[bool]
    top: NotRequired[bool]
    no_wrap: NotRequired[bool]


class ItemSection(TextElement):
    _ITEM_SECTION_PROPS = {
        'avatar': 'avatar',
        'thumbnail': 'thumbnail',
        'side': 'side',
        'top': 'top',
        'no_wrap': 'no-wrap'
    }

    def __init__(self, text: str='', **kwargs: ItemSectionKwargs):
        """List Item Section

        Creates an item section based on Quasar's
        `QItemSection <https://quasar.dev/vue-components/list-and-list-items#qitemsection-api>`_ component.
        The section should be placed inside a ``ui.item`` element.

        :param text: text to be displayed
        :param kwargs: Additional keyword arguments:
            - avatar (bool): avatar section
            - thumbnail (bool): thumbnail section
            - side (bool): side section
            - top (bool): top aligned section
            - no_wrap (bool): prevents text wrapping
        """
        super().__init__(tag='q-item-section', text=text)

        for py_prop, vue_prop in self._ITEM_SECTION_PROPS.items():
            if py_prop in kwargs:
                self._props[vue_prop] = kwargs[py_prop]
