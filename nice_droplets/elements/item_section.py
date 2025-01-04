from typing import Optional

from nicegui import ui


class ItemSection(ui.element, component='item_section.js'):
    def __init__(self, *,
                 avatar: bool = False,
                 thumbnail: bool = False,
                 side: bool = False,
                 top: bool = False,
                 no_wrap: bool = False,
                 overline: Optional[str] = None,
                 label: Optional[str] = None,
                 caption: Optional[str] = None):
        super().__init__()
        self._props['avatar'] = avatar
        self._props['thumbnail'] = thumbnail
        self._props['side'] = side
        self._props['top'] = top
        self._props['noWrap'] = no_wrap
        self._props['overline'] = overline
        self._props['label'] = label
        self._props['caption'] = caption
