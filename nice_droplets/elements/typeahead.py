from typing import Any, Callable
from nicegui import ui
from nicegui.element import Element
from nicegui.events import ValueChangeEventArguments, GenericEventArguments

from nice_droplets.elements.popover import Popover
from nice_droplets.elements.search_list import SearchList


class Typeahead(Popover):
    """A typeahead component that shows suggestions as you type.
    
    This component extends the Popover component to provide typeahead functionality
    for any ValueElement (like input, select, etc.).
    """

    def __init__(self,
                 *,
                 on_search: Callable[[str], list[Any]] | None = None,
                 min_chars: int = 1,
                 debounce_ms: int = 300,
                 item_label: Callable[[Any], str] | None = None,
                 on_select: Callable[[Any], None] | None = None,
                 observe_parent: bool = True,
                 ):
        """Initialize the typeahead component.
        
        Args:
            on_search: Callback function that takes a search string and returns a list of suggestions
            min_chars: Minimum number of characters before triggering search
            debounce_ms: Debounce time in milliseconds for search
            item_label: Function to convert an item to its display string (defaults to str)
            on_select: Callback function when an item is selected
            observe_parent: Whether to automatically attach to parent element
        """
        super().__init__(
            show_events=['focus', 'input'],
            hide_events=['blur'],
            docking_side='bottom left',
            observe_parent=observe_parent,
            default_style=True
        )

        self.keep_hidden = True

        # Create the search list
        with self:
            self._search_list = SearchList(
                on_search=on_search,
                min_chars=min_chars,
                debounce_ms=debounce_ms,
                item_label=item_label,
                on_select=lambda item: self._handle_item_select(item)
            )

        # Setup event handlers
        if observe_parent:
            parent = ui.context.slot.parent
            parent.on_value_change(self._handle_input_change)
            parent.on('keydown', self._handle_key)

    def _handle_key(self, e: GenericEventArguments) -> None:
        """Handle keyboard events."""
        if self._search_list.handle_key(e):
            pass  # TODO prevent default argument

    def _handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input value changes."""
        self._search_list.handle_input_change(e)
        self.keep_hidden = len(str(e.value or '')) < self._search_list._min_chars

    def _handle_item_select(self, item: Any) -> None:
        """Handle when a suggestion item is selected."""
        if on_select:
            on_select(item)
        self.hide()

    def add_target(self, element: Element):
        """Add a target element to the typeahead."""
        super().add_target(element)
        if hasattr(element, 'on_value_change'):
            element.on_value_change(self._handle_input_change)
        element.on('key', self._handle_key)

    def remove_target(self, element: Element):
        """Remove a target element from the typeahead."""
        super().remove_target(element)
