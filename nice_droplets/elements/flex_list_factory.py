from typing import Any, Optional, TypeVar

from nicegui import ui

from nice_droplets.elements.item import Item
from nice_droplets.elements.itemlist import ItemList

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


class ItemListFactory(FlexListFactory):
    """Factory for creating item lists using Quasar components"""
    def __init__(self, *, bordered: bool = False, separator: bool = True, padding: bool = True):
        super().__init__()
        self._bordered = bordered
        self._separator = separator
        self._padding = padding
            
    def create_container(self) -> ui.element:
        self._container = ItemList(
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
            disabled = data.get('disabled', False)
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
            disabled = getattr(data, 'disabled', False)
                
        # Create the item
        item = Item(clickable=True, disable=disabled, ripple=True)
            
        # Add icon or avatar if provided
        if icon or avatar:
            with item:
                section = item.add_section(avatar=True)
                if icon:
                    with section:
                        ui.avatar(
                            icon=icon,
                            color=avatar_color,
                            text_color=avatar_text_color,
                            square=avatar_square,
                            rounded=avatar_rounded
                        )
                elif avatar:
                    with section:
                        with ui.avatar(
                            color=avatar_color,
                            text_color=avatar_text_color,
                            square=avatar_square,
                            rounded=avatar_rounded
                        ):
                            ui.image(avatar)
                
        # Add main content section
        with item:
            section = item.add_section(
                overline=overline if overline else None,
                label=title,
                caption=subtitle if subtitle else None
            )
                    
        # Add timestamp if provided
        if stamp:
            with item:
                with item.add_section(side=True) as section:
                    section.classes('items-end')
                    ui.label(stamp).classes('text-caption')
                    
        self._container.add(item)
        return item

    def _select_item(self, item: ui.element) -> None:
        if not self._is_item_disabled(item):
            item.classes('bg-primary text-white')
        
    def _deselect_item(self, item: ui.element) -> None:
        item.classes(remove='bg-primary text-white')


class TableItemFactory(FlexListFactory):
    def __init__(self):
        super().__init__()
        
    def create_container(self) -> ui.element:
        self._container = ui.table(rows=[], columns=[])
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        # This is just a placeholder since we handle items differently in tables
        return ui.element('div')

    def _select_item(self, item: ui.element) -> None:
        if self._container:
            self._container.selected = [self._index]
    
    def _deselect_item(self, item: ui.element) -> None:
        if self._container:
            self._container.selected = []
            
    def clear(self) -> None:
        super().clear()
        if self._container:
            self._container.rows = []
            self._container.columns = []
            
    def update_items(self, items: list[Any]) -> None:
        """Update displayed items in table format"""
        self.clear()
        self._items = items
        
        if not items:
            return
            
        # Extract columns from the first item
        sample_item = items[0]
        if isinstance(sample_item, dict):
            # Filter out special keys
            columns = [
                {'name': key, 'label': key.title(), 'field': key}
                for key in sample_item.keys()
                if key not in ('disabled',)
            ]
        else:
            # For non-dict items, raise an error
            raise ValueError('Non-dict items are not supported in table view')
            
        # Convert items to table rows
        rows = []
        for item in items:
            if isinstance(item, dict):
                # Filter out special keys
                row = {k: v for k, v in item.items() if k not in ('disabled',)}
            else:
                row = {'value': str(item)}
            rows.append(row)
            
        if self._container:
            self._container.columns = columns
            self._container.rows = rows
            self._container.on('select', lambda e: self._handle_table_select(e))

    def _handle_table_select(self, e: Any) -> None:
        """Handle table selection event"""
        if e.args.get('selected', None):
            self.index = e.args['selected'][0]
        else:
            self.index = -1
