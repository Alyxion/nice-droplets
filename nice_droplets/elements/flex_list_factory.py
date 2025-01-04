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
        self._click_handler: list[Callable[[FlexListItemClickedArguments], None]] = [on_item_click] if on_item_click else []
        
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
    
    def create_container(self) -> ui.element:
        """Create and return the container element"""
        raise NotImplementedError()
    
    def create_item(self, data: Any) -> ui.element:
        """Create and return an item element for the given data"""
        raise NotImplementedError()    
    
    def _handle_index_changed(self) -> None:
        """Called when the current index changes"""
        if 0 <= self._previous_index < len(self._item_elements):
            self._deselect_item(self._item_elements[self._previous_index])
        if 0 <= self._index < len(self._item_elements):
            self._select_item(self._item_elements[self._index])

    def _select_item(self, item: ui.element) -> None:
        """Apply selection styling to an item"""
        raise NotImplementedError()
    
    def _deselect_item(self, item: ui.element) -> None:
        """Remove selection styling from an item"""
        raise NotImplementedError()

    def is_item_disabled(self, item: Any) -> bool:
        """Check if an item is disabled based on its data"""
        if isinstance(item, dict):
            return item.get('disabled', False)
        elif hasattr(item, 'disabled'):
            return bool(item.disabled)
        return False

    def _enable_item(self, item: ui.element) -> None:
        item.classes('cursor-pointer hover:bg-gray-100', 
                    remove='cursor-not-allowed opacity-50')
    
    def _disable_item(self, item: ui.element) -> None:
        item.classes('cursor-not-allowed opacity-50', 
                    remove='cursor-pointer hover:bg-gray-100')

    def _update_item_state(self, item: ui.element, data: Any) -> None:
        """Update item's visual state based on its disabled status"""
        if self.is_item_disabled(data):
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
                    self._update_item_state(item_element, item_data)
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

    def _select_item(self, item: ui.element) -> None:
        item.classes('bg-primary text-white', remove='hover:bg-gray-100')
    
    def _deselect_item(self, item: ui.element) -> None:
        item.classes('hover:bg-gray-100', remove='bg-primary text-white')


class ItemListFactory(FlexListFactory):
    """Factory for creating item lists using Quasar components"""
    def __init__(self, *, bordered: bool = False, separator: bool = True, padding: bool = True):
        super().__init__()
        self._bordered = bordered
        self._separator = separator
        self._padding = padding
            
    def create_container(self) -> ui.element:
        self._container = List(
            bordered=self._bordered,
            separator=self._separator,
            padding=self._padding
        )
        return self._container
        
    def create_item(self, data: Any) -> ui.element:
        # Extract item properties
        if isinstance(data, dict):
            title = str(data.get('label', data.get('title', '')))
            subtitle = str(data.get('subtitle', ''))
            overline = str(data.get('overline', ''))
            icon = data.get('icon', None)
            avatar = data.get('avatar', None)
            avatar_color = data.get('avatar_color', None)
            avatar_text_color = data.get('avatar_text_color', None)
            avatar_square = data.get('avatar_square', False)
            avatar_rounded = data.get('avatar_rounded', False)
            stamp = data.get('stamp', None)
        else:
            title = str(data)
            subtitle = ''
            overline = ''
            icon = None
            avatar = None
            avatar_color = None
            avatar_text_color = None
            avatar_square = False
            avatar_rounded = False
            stamp = None
                
        # Create the item
        item = Item(clickable=True, ripple=True)
            
        # Add icon or avatar if provided
        if icon or avatar:
            with item:
                with ItemSection(avatar=True) as section:
                    if icon:
                        ui.avatar(
                            icon=icon,
                            color=avatar_color,
                            text_color=avatar_text_color,
                            square=avatar_square,
                            rounded=avatar_rounded
                        )
                    elif avatar:
                        with ui.avatar(
                            color=avatar_color,
                            text_color=avatar_text_color,
                            square=avatar_square,
                            rounded=avatar_rounded
                        ):
                            ui.image(avatar)
                
        # Add main content section
        with item:
            with ItemSection(
                overline=overline if overline else None,
                label=title,
                caption=subtitle if subtitle else None
            ):
                pass
                    
        # Add timestamp if provided
        if stamp:
            with item:
                with ItemSection(side=True) as section:
                    section.classes('items-end')
                    ui.label(stamp).classes('text-caption')

        # Add click handler
        item.on('click', lambda _: self.handle_item_click(item))
                    
        return item

    def _select_item(self, item: ui.element) -> None:
        item.classes('bg-primary text-white')
        
    def _deselect_item(self, item: ui.element) -> None:
        item.classes(remove='bg-primary text-white')


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

    def _select_item(self, item: ui.element) -> None:
        if self._table:
            self._table.selected = [self._index]
    
    def _deselect_item(self, item: ui.element) -> None:
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
