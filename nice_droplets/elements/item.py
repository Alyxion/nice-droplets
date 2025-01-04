from typing import Any, Optional, Self

from nicegui import ui

from .item_section import ItemSection


class Item(ui.element, component='item.js'):
    def __init__(self, *, clickable: bool = True, disable: bool = False, ripple: bool = True):
        super().__init__()
        self._props['clickable'] = clickable
        self._props['disable'] = disable
        self._props['ripple'] = ripple
        
    def add_section(self, *, 
                   avatar: bool = False,
                   thumbnail: bool = False,
                   side: bool = False,
                   top: bool = False,
                   no_wrap: bool = False,
                   overline: Optional[str] = None,
                   label: Optional[str] = None,
                   caption: Optional[str] = None) -> ItemSection:
        section = ItemSection(
            avatar=avatar,
            thumbnail=thumbnail,
            side=side,
            top=top,
            no_wrap=no_wrap,
            overline=overline,
            label=label,
            caption=caption
        )
        return section
