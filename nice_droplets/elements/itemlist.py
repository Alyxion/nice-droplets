from typing import Optional, Self

from nicegui import ui

from .item import Item


class ItemList(ui.element, component='itemlist.js'):
    def __init__(self, *, bordered: bool = False, separator: bool = False, padding: bool = True):
        super().__init__()
        self._props['bordered'] = bordered
        self._props['separator'] = separator
        self._props['padding'] = padding
        self._items: list[Item] = []
            
    def add(self, item: Item) -> Self:
        self._items.append(item)
        return self
        
    def clear(self) -> None:
        super().clear()
        self._items = []
