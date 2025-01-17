from typing import Any

from nicegui import ui

from .flex_list_factory import FlexListFactory

class FlexDefaultFactory(FlexListFactory, short_name="Default"):
    """Factory for creating simple label-based list items"""
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
            item.on('click', lambda _: self.handle_item_click(item))
        return item

    def select_item(self, index: int) -> None:
        """Apply selection styling to an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes('bg-primary text-white', remove='hover:bg-gray-100')
    
    def deselect_item(self, index: int) -> None:
        """Remove selection styling from an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes('hover:bg-gray-100', remove='bg-primary text-white')
