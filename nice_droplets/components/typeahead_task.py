from typing import Any, Callable, TypeVar

from .task import Task

T = TypeVar('T')

class SearchTask(Task[list[T]]):
    """A task for performing searches.
    
    This task executes a search function with a query string and returns a list of results.
    It can be cancelled if the search is no longer needed.
    """
    def __init__(self, 
                 search_fn: Callable[[str], list[T]], 
                 query: str):
        """Initialize the search task.
        
        Args:
            search_fn: Function that performs the search, taking a query string and returning results
            query: The search query string
        """
        super().__init__()
        self._search_fn = search_fn
        self._query = query

    def execute(self) -> list[T]:
        """Execute the search if not cancelled.
        
        Returns:
            List of search results, or empty list if cancelled
        """
        if self.is_cancelled:
            return []
        return self._search_fn(self._query)
