import inspect
from typing import Any, Callable

from nicegui import ui

from nice_droplets.events import FlexFactoryItemClickedArguments
from nice_droplets.elements.item import Item as item
from nice_droplets.elements.list import List as list
from nice_droplets.elements.item_section import ItemSection as item_section
from .flex_list_factory import FlexListFactory

class FlexItemListFactory(FlexListFactory, short_name="Item"):
    
    def __init__(self, on_item_click: Callable[[FlexFactoryItemClickedArguments], None] | None = None, **kwargs):
        """FlexItemListFactory

        Factory for creating item lists with advanced features like title, subtitle and avatar.

        :param on_item_click: Optional callback for handling item clicks        
        :param kwargs: Additional keyword arguments:
            - bordered (bool): applies a border to the list
            - separator (bool): applies a separator between items
            - padding (bool): applies default padding to the list
            - ... and other arguments supported by list
        """
        super().__init__(on_item_click=on_item_click)
        # Extract list-specific kwargs
        self._list_kwargs = kwargs

    def create_container(self) -> ui.element:
        """Create and return the container element"""
        self._container = list(**self._list_kwargs)
        return self._container

    def setup_item(self, item: item, data: Any) -> ui.element:
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
                with item_section(avatar=True):
                    if avatar.startswith(('http://', 'https://')):
                        ui.image(avatar).classes(f'w-8 h-8{"rounded-full" if avatar_round else ""}')
                    else:
                        ui.icon(avatar).classes('text-2xl')

            # Add text content
            with item_section():
                if title:
                    ui.label(title).classes('text-body1')
                if subtitle:
                    ui.label(subtitle).classes('text-caption text-grey-7')        

        return item

    def create_item(self, data: Any) -> ui.element:
        # Create the item
        item_obj = item(
            clickable=not self.is_item_disabled(data),
            disable=self.is_item_disabled(data),
        )

        """Create and return an item element for the given data"""
        self.setup_item(item_obj, data)
        # Add click handler
        item_obj.on('click', lambda _: self.handle_item_click(item_obj))
                    
        return item_obj

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
