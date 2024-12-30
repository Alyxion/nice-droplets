from typing import Any, Callable
from nicegui import ui
from nicegui.element import Element
from nicegui.events import ValueChangeEventArguments, GenericEventArguments


class SearchList(Element):
    """A component that handles search and displays a list of results with selection capabilities."""

    def __init__(self,
                 *,
                 on_search: Callable[[str], list[Any]] | None = None,
                 min_chars: int = 1,
                 debounce_ms: int = 300,
                 item_label: Callable[[Any], str] | None = None,
                 on_select: Callable[[Any], None] | None = None,
                 ):
        """Initialize the search list component.
        
        Args:
            on_search: Callback function that takes a search string and returns a list of suggestions
            min_chars: Minimum number of characters before triggering search
            debounce_ms: Debounce time in milliseconds for search
            item_label: Function to convert an item to its display string (defaults to str)
            on_select: Callback function when an item is selected
        """
        super().__init__('div')
        self.classes('flex flex-col gap-1 min-w-[200px]')

        self._on_search = on_search
        self._min_chars = min_chars
        self._debounce_ms = debounce_ms
        self._item_label = item_label or str
        self._on_select = on_select
        self._items: list[Any] = []
        self._selected_index: int = -1
        self._suggestion_elements: list[ui.element] = []

        # Create the suggestion list container
        with self:
            self._suggestions_container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')

    def _update_selection(self) -> None:
        """Update the visual selection of items."""
        for i, item_element in enumerate(self._suggestion_elements):
            if i == self._selected_index:
                item_element.classes('bg-primary text-white', remove='hover:bg-gray-100')
            else:
                item_element.classes('hover:bg-gray-100', remove='bg-primary text-white')

    def clear(self) -> None:
        """Clear all suggestions."""
        self._suggestions_container.clear()
        self._items = []
        self._suggestion_elements = []
        self._selected_index = -1

    def update_items(self, items: list[Any]) -> None:
        """Update the suggestions list."""
        self.clear()
        self._items = items
        with self._suggestions_container:
            for item in items:
                label = self._item_label(item)
                item_element = ui.element('div').classes(
                    'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors'
                ).on('click', lambda i=item: self._handle_item_click(i))
                with item_element:
                    ui.label(label).classes('w-full text-left')
                self._suggestion_elements.append(item_element)

    def handle_key(self, e: GenericEventArguments) -> bool:
        """Handle keyboard events.
        
        Returns:
            bool: True if the key was handled, False otherwise
        """
        if not self._items:
            return False

        key = e.args['key']
        handled = True

        if key == 'Enter':
            if self._selected_index >= 0 and self._selected_index < len(self._items):
                self._handle_item_click(self._items[self._selected_index])
            elif self._items:  # If no item is selected, select the first one
                self._handle_item_click(self._items[0])
        elif key == 'ArrowDown':
            self._selected_index = min(self._selected_index + 1, len(self._items) - 1)
            self._update_selection()
        elif key == 'ArrowUp':
            self._selected_index = max(self._selected_index - 1, -1)
            self._update_selection()
        else:
            handled = False

        return handled

    def handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input value changes."""
        value = str(e.value or '')
        if len(value) < self._min_chars:
            self.clear()
            return

        if self._on_search:
            items = self._on_search(value)
            self.update_items(items)

    def _handle_item_click(self, item: Any) -> None:
        """Handle when a suggestion item is clicked."""
        if self._on_select:
            self._on_select(item)
