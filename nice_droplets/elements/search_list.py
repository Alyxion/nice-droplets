from typing import Any, Callable, TypeVar
from nicegui import ui
from nicegui.events import ValueChangeEventArguments, GenericEventArguments
from threading import Thread

from nice_droplets.components import SearchTask

T = TypeVar('T')

class SearchList(ui.element):
    """A list component that shows search results with keyboard navigation."""

    def __init__(self,
                 *,
                 on_search: Callable[[str], SearchTask[Any]] | None = None,
                 min_chars: int = 1,
                 debounce_ms: int = 300,
                 item_label: Callable[[Any], str] | None = None,
                 on_select: Callable[[Any], None] | None = None,
                 poll_interval_ms: int = 100,
                 ):
        """Initialize the search list component.
        
        Args:
            on_search: Function that creates a search task for a given query
            min_chars: Minimum number of characters before triggering search
            debounce_ms: Debounce time in milliseconds for search
            item_label: Function to convert an item to its display string (defaults to str)
            on_select: Callback function when an item is selected
            poll_interval_ms: How often to check for search results in milliseconds
        """
        super().__init__()
        self._on_search = on_search
        self._min_chars = min_chars
        self._debounce_ms = debounce_ms
        self._item_label = item_label or str
        self._on_select = on_select
        self._poll_interval_ms = poll_interval_ms
        self._items: list[Any] = []
        self._suggestion_elements: list[ui.element] = []
        self._selected_index = -1
        self._current_task: SearchTask[Any] | None = None
        self._poll_timer: ui.timer | None = None

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
        if self._current_task:
            self._current_task.cancel()
            self._current_task = None
        if self._poll_timer:
            self._poll_timer.deactivate()
            self._poll_timer = None

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
            True if the event was handled, False otherwise
        """
        key = e.args.get('key', '')
        handled = True

        if key == 'ArrowDown':
            if self._selected_index < len(self._items) - 1:
                self._selected_index += 1
                self._update_selection()
        elif key == 'ArrowUp':
            if self._selected_index > 0:
                self._selected_index -= 1
                self._update_selection()
        elif key == 'Enter':
            if 0 <= self._selected_index < len(self._items):
                self._handle_item_click(self._items[self._selected_index])
        else:
            handled = False

        return handled

    def handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input value changes."""
        value = str(e.value or '')
        
        # Cancel any existing search
        if self._current_task:
            self._current_task.cancel()
            self._current_task = None
        
        if len(value) < self._min_chars:
            self.clear()
            return

        if not self._on_search:
            return

        # Create and start new search task
        self._current_task = self._on_search(value)
        Thread(target=self._current_task.run).start()
        
        # Start polling for results
        if self._poll_timer:
            self._poll_timer.deactivate()
        self._poll_timer = ui.timer(self._poll_interval_ms / 1000, 
                                  self._check_search_results,
                                  active=True)

    def _check_search_results(self) -> None:
        """Check if search results are available and update the UI."""
        if not self._current_task or not self._current_task.is_done:
            return
            
        if self._poll_timer:
            self._poll_timer.deactivate()
            self._poll_timer = None
            
        if self._current_task.has_error:
            print(f"Search error: {self._current_task.error}")
            self.clear()
            return
            
        results = self._current_task.result or []
        self._current_task = None
        self.update_items(results)

    def _handle_item_click(self, item: Any) -> None:
        """Handle when a suggestion item is clicked."""
        if self._on_select:
            self._on_select(item)
