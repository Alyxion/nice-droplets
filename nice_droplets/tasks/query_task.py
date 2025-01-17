import time
from typing import Any, Awaitable, Callable, TypeVar, Union
from threading import RLock
import asyncio

from pydantic import BaseModel, Field

from .task import Task


class QueryTask(Task):
    """A generic query task.

    This task executes a query function with a query string and returns a list of results.
    It can be cancelled if the query is no longer needed.

    The query logic can be implemented as a function that takes a query string and returns a list of results,
    altenatively either the execute or execute_async method can be overridden to perform the query asynchronously.
    """

    def __init__(
        self,
        search_fn: (Callable[[str], list[Any]] | Callable[[str], Awaitable[list[Any]]] | None) = None,
        query: str | None = None,
        max_elements: int = -1,
        first_element_index: int = 0,
    ):
        """Initialize the query task.        

        :param search_fn: The query function to execute, can be sync or async.

            The simplest version is a function that takes a query string and returns a list of results.
            The more advanced version is a function that takes a SearchParameters object and returns a SearchResults object.
        :param query: The query string to pass to the search function.
        :param search_fn: The search function to execute, can be sync or async.
        :param max_elements: The maximum number of elements to return from the search function.
        :param first_element_index: The index of the first element to return from the search function.
        """
        super().__init__()
        self.max_elements = max_elements
        self._data_lock = RLock()
        self._query: str | None = query
        self._elements: list[Any] = []
        self._first_element_index: int = first_element_index
        self._total_elements: int = 0
        self._more_elements: bool = False
        self._search_fn: Callable[[str], list[Any]] | Callable[[str], Awaitable[list[Any]]] | None = search_fn  # type: ignore

    def add_elements(self, elements: list[Any]):
        """Add elements to the query results."""
        with self._data_lock:
            # Apply first_element_index
            elements = elements[self._first_element_index:]
            
            if self.max_elements == -1:
                self._elements.extend(elements)
            else:
                if len(self._elements) < self.max_elements:
                    remaining_space = self.max_elements - len(self._elements)
                    self._elements.extend(elements[:remaining_space])
                    if len(elements) > remaining_space:
                        self._more_elements = True
                else:                    
                    self._more_elements = True

    def set_elements(self, elements: list[Any]):
        """Set the query results."""
        with self._data_lock:
            # Apply first_element_index
            elements = elements[self._first_element_index:]
            
            if self.max_elements == -1 or len(elements) <= self.max_elements:
                self._elements = elements
            else:
                self._elements = elements[: self.max_elements]
                self._more_elements = True

    def execute(self):
        """Execute the query if not cancelled.

        Overwrite with custom sync query logic if needed.

        :return: A list of query results.
        """
        if self.is_async:
            raise NotImplementedError("Use execute_async for async search functions")
        if self._search_fn and self._query is not None:
            result = self._search_fn(self._query)  # type: ignore
            self._total_elements = len(result)
            self.set_elements(result)

    async def execute_async(self):
        """Execute the query asynchronously if not cancelled.

        Overwrite with custom async query logic if needed.

        :return: A list of query results.
        """
        if not self.is_async:
            raise NotImplementedError("Use execute for sync search functions")
        if self._search_fn and self._query is not None:
            result = await self._search_fn(self._query)  # type: ignore
            self._total_elements = len(result)
            self.set_elements(result)

    @property
    def elements(self) -> list[Any]:
        """Get the query results if available, None otherwise."""
        if not self.is_done:
            return []
        return self._elements

    @property
    def more_elements(self) -> bool:
        """Check if there are more elements available."""
        return self._more_elements

    @property
    def first_element_index(self) -> int:
        """Get the index of the first element."""
        return self._first_element_index

    @property
    def total_elements(self) -> int:
        """Get the total number of elements (available in the source such as a database but not necessarily returned)."""
        return self._total_elements

    @total_elements.setter
    def total_elements(self, value: int):
        self._total_elements = value

    @property
    def is_async(self) -> bool:
        """Check if the query function is executed asynchronously."""

        # check if the execute function were overridden
        if self.execute.__func__ != QueryTask.execute:
            return False
        if self.execute_async.__func__ != QueryTask.execute_async:
            return True
        return self._search_fn is not None and asyncio.iscoroutinefunction(self._search_fn)
