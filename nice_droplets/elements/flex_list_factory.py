from typing import Any, Callable, Optional, TypeVar

from nicegui import ui
from nicegui.events import handle_event

from nice_droplets.elements.item import Item
from nice_droplets.elements.list import List
from nice_droplets.elements.item_section import ItemSection
from nice_droplets.events import FlexFactoryItemClickedArguments

T = TypeVar('T')

class FlexListFactory:
    def __init__(self, *, on_item_click: Optional[Callable[[FlexFactoryItemClickedArguments], None]] = None):
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


class ItemListFactory(FlexListFactory):
    """Factory for creating item lists with basic features like title, subtitle and avatar."""

    def __init__(self, bordered: bool = False, separator: bool = True, padding: bool = True):
        super().__init__()
        self.bordered = bordered
        self.separator = separator
        self.padding = padding
        
        

    def create_container(self) -> ui.element:
        """Create and return the container element"""
        self._container = List(
            bordered=self.bordered,
            separator=self.separator,
            padding=self.padding,
        )
        return self._container

    def setup_item(self, item: Item, data: Any) -> ui.element:
        # Extract basic properties
        title = None
        subtitle = None
        avatar = None
        avatar_round = False

        if isinstance(data, str):
            title = data
        elif isinstance(data, dict):
            title = data.get('title', data.get('label', ''))
            subtitle = data.get('subtitle', data.get('caption', ''))
            avatar = data.get('avatar', data.get('icon', ''))
            avatar_round = data.get('avatar_round', False)
        else:
            title = str(data)

        with item:
            # Add avatar if provided
            if avatar:
                with ItemSection(avatar=True):
                    if avatar.startswith(('http://', 'https://')):
                        ui.image(avatar).classes(f'w-8 h-8{"rounded-full" if avatar_round else ""}')
                    else:
                        ui.icon(avatar).classes('text-2xl')

            # Add text content
            with ItemSection():
                if title:
                    ui.label(title).classes('text-body1')
                if subtitle:
                    ui.label(subtitle).classes('text-caption text-grey-7')        

        return item

    def create_item(self, data: Any) -> ui.element:
        # Create the item
        item = Item(
            clickable=not self.is_item_disabled(data),
            disable=self.is_item_disabled(data),
        )

        """Create and return an item element for the given data"""
        self.setup_item(item, data)
        # Add click handler
        item.on('click', lambda _: self.handle_item_click(item))
                    
        return item

    def select_item(self, index: int) -> None:
        """Apply selection styling to an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].props(add_active=True)

    def deselect_item(self, index: int) -> None:
        """Remove selection styling from an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].props(remove_active=True)

    def disable_item(self, index: int) -> None:
        """Apply disabled styling to an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes(add='disabled')

    def enable_item(self, index: int) -> None:
        """Remove disabled styling from an item at the given index"""
        if 0 <= index < len(self._item_elements):
            self._item_elements[index].classes(remove='disabled')


class TableItemFactory(FlexListFactory):
    def __init__(self):
        super().__init__()
        self._table = None
        
    def create_container(self) -> ui.element:
        self._container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        # Items are handled in update_items
        return None

    def select_item(self, index: int) -> None:
        if self._table:
            if self._index < 0:
                self._table.selected = []
            else:
                self._table.selected = [self._items[self._index]]
    
    def deselect_item(self, index: int) -> None:
        if self._table:
            self._table.selected = []
            
    def clear(self) -> None:
        super().clear()
        self._container.clear()
        self._table = None
        self._rows = []
            
    def update_items(self, items: list[Any]) -> None:
        """Update displayed items in table format"""
        self.clear()
        self._items = items
        self._rows = []
        self._row_dict = {}
        
        if not items:
            return
            
        # Extract columns from the first item
        sample_item = items[0]
        if isinstance(sample_item, dict):
            columns = [
                {'name': key, 'label': key.title(), 'field': key}
                for key in sample_item.keys()
            ]
            rows = [item.copy() for item in items]
        else:
            # For dataclass objects, convert to dict
            data_dict = sample_item.to_dict()
            columns = [
                {'name': key, 'label': key.title(), 'field': key}
                for key in data_dict.keys()
            ]
            rows = [item.to_dict() for item in items]

        # add invisible key column to every row
        for index, row in enumerate(rows):
            row['_index'] = index

        self._rows = rows
            
        # Create table with rows and columns
        with self._container:
            self._table = ui.table(
                columns=columns,
                rows=rows,                
            )
            
        # Handle row clicks
        def on_row_click(e: Any) -> None:
            if len(e.args) < 2:
                return
            element = e.args[1]
            if not "_index" in element:
                return
            row_index = element['_index']                
            if not self.is_item_disabled(row_index):
                self.handle_item_click(row_index)
    
        self._table.on('row-click', on_row_click)
