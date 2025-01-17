from typing import Any, Callable, Union
from nicegui.events import ValueChangeEventArguments, Handler

from nice_droplets.tasks.query_task import QueryTask
from nice_droplets.components.search_manager import SearchManager, SearchResultHandler
from nice_droplets.events import SearchListContentUpdateEventArguments
from nice_droplets.factories import FlexListFactory
from nice_droplets.elements.flex_list import FlexList


class SearchList(FlexList, SearchResultHandler):
    """List component showing search results with keyboard navigation"""

    def __init__(self,
                 *,
                 on_search: Callable[[str], QueryTask] | None = None,
                 min_chars: int = 1,
                 debounce: float = 0.3,
                 on_click: Callable[[Any], None] | None = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 poll_interval: float = 0.1,
                 factory: Union[FlexListFactory, str] | None = None
                 ):
        """Initialize the search list.
        
        :param on_search: Function that creates a search task for a query.
        :param min_chars: Minimum number of characters required to start a search.
        :param debounce: Time to wait before executing a search after input changes.
        :param on_click: Function to call when an item is clicked.
        :param on_content_update: Handler for content update events.
        :param poll_interval: Interval for polling search results.
        :param factory: Factory to use for creating the flex views. Can be either a FlexListFactory instance
                      or a string name (e.g., "Item", "Table", "Default", or their capital letter versions like "I", "T", "D")
        """
        super().__init__(
            on_click=on_click,
            on_content_update=on_content_update,
            factory=factory
        )
        self._on_search = on_search
            
        self._search_manager = SearchManager(
            on_search=self._on_search,
            result_handler=self,
            min_chars=min_chars,
            debounce=debounce,
            poll_interval=poll_interval
        )

    def set_search_handler(self, on_search: Callable[[str], QueryTask] | None) -> None:
        """Set the search handler for the search list."""
        self._on_search = on_search
        self._search_manager.set_search_handler(on_search)

    def set_search_query(self, query: str) -> None:
        """Handle input changes"""
        if len(query) < self._search_manager._min_chars:
            self.items = []
            return
        self._search_manager.handle_search(query)

    def on_search_started(self) -> None:
        """Called when a search is started."""
        pass

    def on_search_error(self, error: Exception) -> None:
        """Called when a search fails."""
        self.clear()

    def on_search_results(self, results: list[Any]) -> None:
        """Called when search results are available."""
        self.update_items(results)

    def cleanup(self) -> None:
        """Clean up resources."""
        super().cleanup()
        self._search_manager.cleanup()
