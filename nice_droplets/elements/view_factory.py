from typing import Any, Optional, TypeVar

from nicegui import ui

T = TypeVar('T')

class FlexListFactory:
    def __init__(self):
        self._index = -1
        self._previous_index = -1
        self._container: Optional[ui.element] = None
        self._items: list[Any] = []
        self._item_elements: list[ui.element] = []
        
    @property
    def index(self) -> int:
        return self._index
    
    @index.setter
    def index(self, value: int) -> None:
        if 0 <= value < len(self._item_elements) and self._is_item_disabled(self._item_elements[value]):
            return
        self._previous_index = self._index
        self._index = value
        self._on_index_changed()
    
    def create_container(self) -> ui.element:
        """Create and return the container element"""
        raise NotImplementedError()
    
    def create_item(self, data: Any) -> ui.element:
        """Create and return an item element for the given data"""
        raise NotImplementedError()
    
    def _on_index_changed(self) -> None:
        """Called when the current index changes"""
        if 0 <= self._previous_index < len(self._item_elements):
            self._deselect_item(self._item_elements[self._previous_index])
        if 0 <= self._index < len(self._item_elements):
            if not self._is_item_disabled(self._item_elements[self._index]):
                self._select_item(self._item_elements[self._index])
    
    def _select_item(self, item: ui.element) -> None:
        """Apply selection styling to an item"""
        raise NotImplementedError()
    
    def _deselect_item(self, item: ui.element) -> None:
        """Remove selection styling from an item"""
        raise NotImplementedError()

    def _enable_item(self, item: ui.element) -> None:
        item.classes('cursor-pointer hover:bg-gray-100', 
                    remove='cursor-not-allowed opacity-50')
    
    def _disable_item(self, item: ui.element) -> None:
        item.classes('cursor-not-allowed opacity-50', 
                    remove='cursor-pointer hover:bg-gray-100')

    def _is_item_disabled(self, item: ui.element) -> bool:
        """Check if an item is disabled based on its data"""
        if hasattr(item, 'data'):
            if isinstance(item.data, dict):
                return item.data.get('disabled', False)
            elif hasattr(item.data, 'disabled'):
                return bool(item.data.disabled)
        return False

    def _update_item_state(self, item: ui.element) -> None:
        """Update item's visual state based on its disabled status"""
        if self._is_item_disabled(item):
            self._disable_item(item)
        else:
            self._enable_item(item)

    def clear(self) -> None:
        """Clear all items"""
        if self._container:
            self._container.clear()
        self._items = []
        self._item_elements = []
        self._index = -1
        self._previous_index = -1

    def update_items(self, items: list[Any]) -> None:
        """Update displayed items"""
        self.clear()
        self._items = items
        if self._container:
            with self._container:
                for item_data in items:
                    item_element = self.create_item(item_data)
                    item_element.data = item_data  # Store the data in the element
                    self._update_item_state(item_element)
                    self._item_elements.append(item_element)

class DefaultFactory(FlexListFactory):
    """Default factory matching original FlexList behavior"""
    def __init__(self):
        super().__init__()
        
    def create_container(self) -> ui.element:
        self._container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        label = str(data) if not isinstance(data, dict) else str(data.get('label', ''))
        item = ui.element('div').classes(
            'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors'
        )
        with item:
            ui.label(label).classes('w-full text-left')
        return item

    def _select_item(self, item: ui.element) -> None:
        item.classes('bg-primary text-white', remove='hover:bg-gray-100')
    
    def _deselect_item(self, item: ui.element) -> None:
        item.classes('hover:bg-gray-100', remove='bg-primary text-white')

class ListItemFactory(FlexListFactory):
    def __init__(self):
        super().__init__()
        
    def create_container(self) -> ui.element:
        self._container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        label = str(data) if not isinstance(data, dict) else str(data.get('label', ''))
        item = ui.element('div').classes(
            'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors'
        )
        with item:
            ui.label(label).classes('w-full text-left')
        return item

    def _select_item(self, item: ui.element) -> None:
        item.classes('bg-blue-100 border-l-4 border-blue-500', remove='hover:bg-gray-100')
    
    def _deselect_item(self, item: ui.element) -> None:
        item.classes('hover:bg-gray-100', remove='bg-blue-100 border-l-4 border-blue-500')

class TableItemFactory(FlexListFactory):
    def __init__(self):
        super().__init__()
        
    def create_container(self) -> ui.element:
        self._container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        item = ui.element('div').classes(
            'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors grid grid-cols-[auto_1fr]'
        )
        if isinstance(data, dict):
            with item:
                for key, value in data.items():
                    if key not in ('disabled', 'label'):
                        ui.label(str(key)).classes('font-bold mr-2')
                        ui.label(str(value)).classes('text-left')
        else:
            with item:
                ui.label(str(data)).classes('w-full text-left col-span-2')
        return item

    def _select_item(self, item: ui.element) -> None:
        item.classes('bg-gray-200 shadow-md', remove='hover:bg-gray-100')
    
    def _deselect_item(self, item: ui.element) -> None:
        item.classes('hover:bg-gray-100', remove='bg-gray-200 shadow-md')

class ViewFactory:
    @staticmethod
    def create_view(view_type: str = 'default') -> FlexListFactory:
        """Create a view container based on the specified type"""
        if view_type == 'default':
            return DefaultFactory()
        elif view_type == 'list':
            return ListItemFactory()
        elif view_type == 'table':
            return TableItemFactory()
        else:
            raise ValueError(f"Unknown view type: {view_type}")
