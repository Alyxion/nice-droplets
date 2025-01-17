from typing import Any, Callable, Optional, TypeVar

from nicegui import ui
from nicegui.events import handle_event

from nice_droplets.events import FlexFactoryItemClickedArguments

T = TypeVar('T')

class FlexListFactory:
    def __init__(self, *, 
                 on_item_click: Optional[Callable[[FlexFactoryItemClickedArguments], None]] = None):
        """Initialize the list factory.
        
        :param on_item_click: Optional callback for handling item clicks
        """
        self._index = -1
        self._previous_index = -1
        self._container: Optional[ui.element] = None
        self._items: list[Any] = []
        self._item_elements: list[ui.element] = []
        self._click_handler: list[Callable[[FlexFactoryItemClickedArguments], None]] = [on_item_click] if on_item_click else []
        
    def create_container(self) -> ui.element:
        """Create and return the container element"""
        raise NotImplementedError()
    
    def create_item(self, data: Any) -> ui.element:
        """Create and return an item element for the given data"""
        raise NotImplementedError()    
    
    @property
    def index(self) -> int:
        return self._index
    
    @index.setter
    def index(self, value: int) -> None:
        self._previous_index = self._index
        self._index = value
        self._handle_index_changed()

    def on_click(self, handler: Callable[[FlexFactoryItemClickedArguments], None]) -> None:
        self._click_handler.append(handler)
    
    def _handle_index_changed(self) -> None:
        """Called when the current index changes"""
        if 0 <= self._previous_index < len(self._items):
            self.deselect_item(self._previous_index)
        if 0 <= self._index < len(self._items):
            self.select_item(self._index)

    def select_item(self, index: int) -> None:
        """Apply selection styling to an item at the given index"""
        raise NotImplementedError()
    
    def deselect_item(self, index: int) -> None:
        """Remove selection styling from an item at the given index"""
        raise NotImplementedError()

    def is_item_disabled(self, item: Any) -> bool:
        """Check if an item is disabled based on its data"""
        if isinstance(item, dict):
            return item.get('disabled', False)
        elif hasattr(item, 'disabled'):
            return bool(item.disabled)
        return False

    def enable_item(self, index: int) -> None:
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes('cursor-pointer hover:bg-gray-100', 
                                              remove='cursor-not-allowed opacity-50')
    
    def disable_item(self, index: int) -> None:
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes('cursor-not-allowed opacity-50', 
                                              remove='cursor-pointer hover:bg-gray-100')

    def _update_item_state(self, index: int, data: Any) -> None:
        """Update item's visual state based on its disabled status"""
        if self.is_item_disabled(data):
            self.disable_item(index)
        else:
            self.enable_item(index)

    def clear(self) -> None:
        """Clear all items"""
        if self._container:
            self._container.clear()
        self._items = []
        self._item_elements = []
        self._index = -1
        self._previous_index = -1

    def handle_item_click(self, element: int | ui.element) -> None:
        if isinstance(element, ui.element):
            index = self._item_elements.index(element)
        else:
            index = element

        element = self._item_elements[index] if index < len(self._item_elements) else None        
        item = self._items[index] if index < len(self._items) else None        
        for handler in self._click_handler:
            handle_event(handler, FlexFactoryItemClickedArguments(sender=self, element=element, index=index, item=item))

    def update_items(self, items: list[Any]) -> None:
        """Update displayed items"""
        self.clear()
        self._items = items
        if self._container:
            with self._container:
                for i, item_data in enumerate(items):
                    item_element = self.create_item(item_data)
                    self._update_item_state(i, item_data)
                    self._item_elements.append(item_element)
