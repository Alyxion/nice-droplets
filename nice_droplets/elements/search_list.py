from typing import Any, Callable
from nicegui.events import ValueChangeEventArguments, Handler

from nice_droplets.components import SearchTask
from nice_droplets.components.search_manager import SearchManager, SearchResultHandler
from nice_droplets.events import SearchListContentUpdateEventArguments
from nice_droplets.elements.flex_list import FlexList, FlexListFactory



class SearchList(FlexList, SearchResultHandler):
    """List component showing search results with keyboard navigation"""

    def __init__(self,
                 *,
                 on_search: Callable[[str], SearchTask] | None = None,
                 min_chars: int = 1,
                 debounce: float = 0.3,
                 on_select: Callable[[Any], None] | None = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 poll_interval: float = 0.1,
                 factory: FlexListFactory | None = None
                 ):
        super().__init__(
            on_select=on_select,
            on_content_update=on_content_update,
            factory=factory
        )
        if on_search and not any(str(t) == 'SearchTask' for t in getattr(on_search, '__annotations__', {}).values()):
            self._on_search = lambda query: SearchTask(on_search, query)
        else:
            self._on_search = on_search
            
        self._search_manager = SearchManager(
            on_search=self._on_search,
            result_handler=self,
            min_chars=min_chars,
            debounce=debounce,
            poll_interval=poll_interval
        )

    def handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input changes"""
        value = str(e.value or '')
        if len(value) < self._search_manager._min_chars:
            return
        self._search_manager.handle_search(value)

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
