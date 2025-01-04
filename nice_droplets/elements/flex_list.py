from typing import Any, Callable, Optional

from nicegui import ui
from nicegui.events import GenericEventArguments, Handler, handle_event

from nice_droplets.events import SearchListContentUpdateEventArguments
from .flex_list_factory import FlexListFactory, DefaultFactory


class FlexList(ui.element):
    """Base list component showing selectable items with keyboard navigation"""

    def __init__(self, *, 
                 items: Optional[list[Any]] = None,
                 factory: Optional[FlexListFactory] = None,
                 on_select: Callable[[Any], None] | None = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 ):
        super().__init__()
        self._on_select = on_select
        self._content_update_handlers = [on_content_update] if on_content_update else []
        self._items: list[Any] = items or []
        self._view = factory or DefaultFactory()
        self._container = self._view.create_container()
        self._props['container_id'] = self._container.id
        
        if items:
            self.update_items(items)

    def on_content_update(self, handler: Handler[SearchListContentUpdateEventArguments]) -> None:
        """Add content update handler"""
        self._content_update_handlers.append(handler)

    def update_items(self, items: list[Any]) -> None:
        """Update the list of items"""
        self._items = items
        self._view.update_items(items)
        
        for handler in self._content_update_handlers:
            self.handle_event(handler, SearchListContentUpdateEventArguments(items))

    @property
    def index(self) -> int:
        """Get the current selection index"""
        return self._view.index
    
    @index.setter
    def index(self, value: int) -> None:
        """Set the current selection index"""
        self._view.index = value
        if self._on_select and 0 <= value < len(self._items):
            self._on_select(self._items[value])
