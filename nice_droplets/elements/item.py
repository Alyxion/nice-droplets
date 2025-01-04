from typing import Any, Optional, Self

from nicegui import ui


class Item(ui.element, component='item.js'):
    def __init__(self, *, clickable: bool = True, disable: bool = False, ripple: bool = True):
        super().__init__()
        self._props['clickable'] = clickable
        self._props['disable'] = disable
        self._props['ripple'] = ripple
