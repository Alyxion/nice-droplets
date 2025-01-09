from typing import Any

from nicegui import ui

from nice_droplets.elements.item import Item
from nice_droplets.elements.list import List
from nice_droplets.elements.item_section import ItemSection
from .flex_list_factory import FlexListFactory

class FlexItemListFactory(FlexListFactory):
    """Factory for creating item lists with advanced features like title, subtitle and avatar."""

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__()
        self._list_kwargs = kwargs

    def create_container(self) -> ui.element:
        """Create and return the container element"""
        self._container = List(**self._list_kwargs)
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
