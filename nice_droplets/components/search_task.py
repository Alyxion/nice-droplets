import time
from typing import Any, Callable

from .task import Task

class SearchTask(Task):
    """A task for performing searches.
    
    This task executes a search function with a query string and returns a list of results.
    It can be cancelled if the search is no longer needed.
    """
    def __init__(self, 
                 search_fn: Callable[[str], list[T]], 
                 query: str):
        """Initialize the search task.
        
        :param search_fn: The search function to execute.
        :param query: The query string to pass to the search function.
        """
        super().__init__()
        self._search_fn = search_fn
        self._query = query

    def execute(self) -> list:
        """Execute the search if not cancelled.
        
        :return: A list of search results.
        """
        if self.is_cancelled:
            return []
        return self._search_fn(self._query)
