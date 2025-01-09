from typing import Optional, Self, TypedDict

from nicegui import ui
from typing_extensions import NotRequired
from nicegui.element import Element


class ListKwargs(TypedDict):
    bordered: NotRequired[bool]
    separator: NotRequired[bool]
    padding: NotRequired[bool]


class List(Element):
    _LIST_PROPS = {
        'bordered': 'bordered',
        'separator': 'separator',
        'padding': 'padding'
    }

    def __init__(self, **kwargs: ListKwargs) -> None:
        """List

        A list element based on Quasar's `QList <https://quasar.dev/vue-components/list-and-list-items#qlist-api>`_ component.
        It provides a container for ``ui.item`` elements.

        :param kwargs: Additional keyword arguments:
            - bordered (bool): applies a border to the list
            - separator (bool): applies a separator between items
            - padding (bool): applies default padding to the list
        """
        super().__init__(tag='q-list')

        for py_prop, vue_prop in self._LIST_PROPS.items():
            if py_prop in kwargs:
                self._props[vue_prop] = kwargs[py_prop]
