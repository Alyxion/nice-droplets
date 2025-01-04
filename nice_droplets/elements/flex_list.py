from typing import Any, Callable, Optional
from dataclasses import dataclass

from nicegui import ui
from nicegui.events import UiEventArguments, Handler, handle_event, GenericEventArguments
from nicegui.dataclasses import KWONLY_SLOTS

from nice_droplets.elements.flex_list_factory import FlexListFactory, DefaultFactory
from nice_droplets.components.hot_key_handler import HotKeyHandler
from nice_droplets.events import SearchListContentUpdateEventArguments, FlexListItemClickedArguments, FlexFactoryItemClickedArguments


class FlexList(ui.element):
    """Base list component showing selectable items with keyboard navigation"""

    def __init__(self, *, 
                 items: Optional[list[Any]] = None,
                 factory: Optional[FlexListFactory] = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 on_select: Handler[FlexListItemClickedArguments] | None = None,
                 ):
        super().__init__()
        self._content_update_handlers = [on_content_update] if on_content_update else []
        self._select_handlers = [on_select] if on_select else []
        self._items: list[Any] = items or []
        self._view = factory or DefaultFactory()
        self._view.on_click(self._handle_item_click)
        self._container = self._view.create_container()
        self._props['container_id'] = self._container.id
        
        self._hot_key_handler = HotKeyHandler({
            'next': {
                'key': 'ArrowDown'
            },
            'previous': {
                'key': 'ArrowUp'
            },
            'confirm': {
                'key': 'Enter'
            },
            'escape': {
                'key': 'Escape'
            }
        })
        
        if items:
            self.update_items(items)

    @property
    def items(self) -> list[Any]:
        return self._items

    @items.setter
    def items(self, value: list[Any]) -> None:
        self.update_items(value)

    def on_content_update(self, handler: Handler[SearchListContentUpdateEventArguments]) -> None:
        """Add content update handler"""
        self._content_update_handlers.append(handler)

    def on_select(self, handler: Handler[FlexListItemClickedArguments]) -> None:
        """Add select handler"""
        self._select_handlers.append(handler)

    def _handle_key(self, e: GenericEventArguments) -> bool:
        """Handle keyboard navigation events.
        
        Returns True if the event was handled.
        """
        if self._hot_key_handler.verify('next', e):
            self._move_selection(1)
            return True
        
        if self._hot_key_handler.verify('previous', e):
            self._move_selection(-1)
            return True
        
        if self._hot_key_handler.verify('confirm', e):
            self._confirm_current()
            return True
            
        if self._hot_key_handler.verify('escape', e):
            self.clear_selection()
            return True
            
        return False

    def _move_selection(self, delta: int) -> None:
        """Move the current selection by delta positions."""
        if not self._items:
            return
            
        new_index = self._view.index + delta
        if new_index < 0:
            new_index = len(self._items) - 1
        elif new_index >= len(self._items):
            new_index = 0
            
        self._update_selection(new_index)

    def _update_selection(self, new_index: int) -> None:
        """Update the current selection to the specified index."""
        self._view.index = new_index

    def _confirm_current(self) -> None:
        """Select the currently highlighted item."""
        if 0 <= self._view.index < len(self._items):
            element = self._view._item_elements[self._view.index] if self._view._item_elements else None
            self._handle_item_click(FlexFactoryItemClickedArguments(sender=self, item=self._items[self._view.index], index=self._view.index, element=element))

    def _handle_item_click(self, e: FlexFactoryItemClickedArguments) -> None:
        """Handle item click events."""
        for handler in self._select_handlers:
            handle_event(handler, FlexListItemClickedArguments(sender=self, client=self.client, item=e.item, index=e.index, element=e.element))

    def update_items(self, items: list[Any]) -> None:
        """Update the list of items"""
        self._items = items
        self._current_index = -1
        self._view.update_items(items)
        for handler in self._content_update_handlers:
            handle_event(handler, SearchListContentUpdateEventArguments(sender=self, client=self.client, items=items))

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._view.index = -1

    def clear(self) -> None:
        """Clear all items"""
        self._items = []
        self._current_index = -1
        self._view.update_items([])        
        for handler in self._content_update_handlers:
            handle_event(handler, SearchListContentUpdateEventArguments(sender=self, client=self.client, items=[]))
