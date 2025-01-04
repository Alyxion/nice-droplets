from typing import Any, Callable
from nicegui import ui
from nicegui.events import GenericEventArguments, Handler, handle_event

from nice_droplets.components.hot_key_handler import HotKeyHandler
from nice_droplets.events import SearchListContentUpdateEventArguments


class FlexList(ui.element):
    """Base list component showing selectable items with keyboard navigation"""

    def __init__(self,
                 *,
                 on_select: Callable[[Any], None] | None = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 ):
        super().__init__()
        self._on_select = on_select
        self._content_update_handlers = [on_content_update] if on_content_update else []
        self._items: list[Any] = []
        self._suggestion_elements: list[ui.element] = []
        self._selected_index = -1
        
        self._hot_key_handler = HotKeyHandler({
            'up': 'ArrowUp',
            'down': 'ArrowDown',
            'select': ['Enter', 'go']  # Add 'go' for Android keyboard's "open" action
        })
        
        with self:
            self._suggestions_container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')

    def on_content_update(self, handler: Handler[SearchListContentUpdateEventArguments]) -> None:
        """Add content update handler"""
        self._content_update_handlers.append(handler)

    @property
    def items(self) -> list[Any]:
        return self._items

    def _update_selection(self) -> None:
        """Update visual selection"""
        for i, item_element in enumerate(self._suggestion_elements):
            if i == self._selected_index:
                item_element.classes('bg-primary text-white', remove='hover:bg-gray-100')
            else:
                item_element.classes('hover:bg-gray-100', remove='bg-primary text-white')                

    def clear(self) -> None:
        """Clear suggestions"""
        self._suggestions_container.clear()
        self._items = []
        self._suggestion_elements = []
        self._selected_index = -1
        self._notify_content_update()

    def update_items(self, items: list[Any]) -> None:
        """Update displayed items"""
        self.clear()
        self._items = items
        with self._suggestions_container:
            for item in items:
                label = str(item)
                item_element = ui.element('div').classes(
                    'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors'
                ).on('click', lambda i=item: self._handle_item_click(i))
                with item_element:
                    ui.label(label).classes('w-full text-left')
                self._suggestion_elements.append(item_element)
        self._notify_content_update()

    def _notify_content_update(self) -> None:
        """Notify content update handlers"""
        args = SearchListContentUpdateEventArguments(sender=self, client=self.client)
        for handler in self._content_update_handlers:
            handle_event(handler, args)

    def handle_key(self, e: GenericEventArguments) -> bool:
        """Handle keyboard navigation"""
        handled = True
        
        if self._hot_key_handler.verify('down', e):
            if self._selected_index < len(self._items) - 1:
                self._selected_index += 1
                self._update_selection()
        elif self._hot_key_handler.verify('up', e):
            if self._selected_index > 0:
                self._selected_index -= 1
                self._update_selection()
        elif self._hot_key_handler.verify('select', e):
            if 0 <= self._selected_index < len(self._items):
                self._handle_item_click(self._items[self._selected_index])
            else:
                if len(self._items) > 0:
                    self._handle_item_click(self._items[0])
        else:
            handled = False
            
        return handled

    def _handle_item_click(self, item: Any) -> None:
        """Handle item selection"""
        if self._on_select:
            self._on_select(item)
