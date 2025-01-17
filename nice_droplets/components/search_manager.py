"""Search manager component for handling search tasks and polling."""

from typing import Any, Callable, Protocol
from nicegui import ui

from nice_droplets.tasks.task_executor import TaskExecutor
from nice_droplets.tasks import QueryTask


class SearchResultHandler(Protocol):
    """Protocol for handling search results."""
    
    def on_search_started(self) -> None:
        """Called when a search is started."""
        ...

    def on_search_error(self, error: Exception) -> None:
        """Called when a search fails."""
        ...

    def on_search_results(self, results: list[Any]) -> None:
        """Called when search results are available."""
        ...

    def on_search_completed(self) -> None:
        """Called when a search is completed."""
        ...


class SearchManager:
    """Manages search tasks and notifies listeners of results."""
    
    def __init__(
        self,
        on_search: Callable[[str], QueryTask] | None = None,
        result_handler: SearchResultHandler | None = None,
        min_chars: int = 1,
        debounce: float = 0.1,
        poll_interval: float = 0.1
    ):
        """Initialize the search manager.
        
        :param on_search: Function that creates a search task for a query.
        :param result_handler: Handler for search results and events.
        :param min_chars: Minimum number of characters required to start a search.
        :param debounce: Time to wait before executing a search after input changes.
        :param poll_interval: Interval for checking search results.
        """
        self._on_search = on_search
        self._result_handler = result_handler
        self._min_chars = min_chars
        self._task_executor = TaskExecutor(debounce)
        self._poll_timer: ui.timer | None = None
        self._poll_interval = poll_interval

    def handle_search(self, query: str) -> None:
        """Handle a new search query.
        
        :param query: The search query string.
        """
        if len(query) < self._min_chars:
            if self._result_handler:
                self._result_handler.on_search_completed()
                self._result_handler.on_search_results([])
            return

        if not self._on_search:
            return

        task = self._on_search(query)
        self._task_executor.schedule(task)
        
        if self._result_handler:
            self._result_handler.on_search_started()
        
        if self._poll_timer:
            self._poll_timer.cancel()
        self._poll_timer = ui.timer(
            interval=self._poll_interval,
            callback=lambda: self._check_results(task),
            active=True
        )

    def _check_results(self, task: QueryTask) -> None:
        """Check if results are available and notify handler.
        
        :param task: The search task to check.
        """
        if task is None:
            return
        if not task.is_done:
            return

        if self._poll_timer:
            self._poll_timer.cancel()
            self._poll_timer = None

        if task.has_error:
            if self._result_handler:
                self._result_handler.on_search_error(task.error)
            return

        if self._result_handler:
            self._result_handler.on_search_results(task.elements)
            self._result_handler.on_search_completed()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self._poll_timer:
            self._poll_timer.cancel()
            self._poll_timer = None
