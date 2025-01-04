from typing import Optional, Self

from nicegui import ui

from .item import Item


class List(ui.element, component='list.js'):
    def __init__(self, *, bordered: bool = False, separator: bool = True, padding: bool = True):
        super().__init__()
        self._props['bordered'] = bordered
        self._props['separator'] = separator
        self._props['padding'] = padding
        self._items: list[Item] = []
            
    def add(self, item: Item) -> Self:
        """Add an item to the list"""
        self._items.append(item)
        item._props['parent_id'] = self.id
        return self
        
    def clear(self) -> None:
        super().clear()
        self._items = []
