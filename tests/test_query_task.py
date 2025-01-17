import pytest
from nicegui import ui, run
from unittest.mock import Mock, patch

from nice_droplets.tasks.query_task import QueryTask
from tests.utils import MockTaskExecutor


# Test data
FRUITS = [
    'Apple', 'Apricot', 'Avocado',
    'Banana', 'Blackberry', 'Blueberry',
    'Cherry', 'Coconut', 'Cranberry',
]


@pytest.mark.asyncio
async def test_query_task_filter_sync():
    """Test QueryTask with synchronous filter function."""
    def filter_fruits(query: str) -> list[str]:
        query = query.lower()
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    executor = MockTaskExecutor()

    # Test exact match
    task = QueryTask(search_fn=filter_fruits, query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert not task.has_error
    assert task.elements == ["Apple"]
    assert task.total_elements == 1

    # Test partial match
    task = QueryTask(search_fn=filter_fruits, query="berry")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Blackberry", "Blueberry", "Cranberry"]
    assert task.total_elements == 3

    # Test case insensitive
    task = QueryTask(search_fn=filter_fruits, query="APPLE")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Apple"]

    # Test no matches
    task = QueryTask(search_fn=filter_fruits, query="xyz")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == []
    assert task.total_elements == 0


@pytest.mark.asyncio
async def test_query_task_filter_async():
    """Test QueryTask with asynchronous filter function."""
    async def filter_fruits(query: str) -> list[str]:
        query = query.lower()
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    executor = MockTaskExecutor()

    # Test exact match
    task = QueryTask(search_fn=filter_fruits, query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert not task.has_error
    assert task.elements == ["Apple"]
    assert task.total_elements == 1

    # Test partial match
    task = QueryTask(search_fn=filter_fruits, query="berry")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Blackberry", "Blueberry", "Cranberry"]
    assert task.total_elements == 3

    # Test case insensitive
    task = QueryTask(search_fn=filter_fruits, query="APPLE")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Apple"]

    # Test no matches
    task = QueryTask(search_fn=filter_fruits, query="xyz")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == []
    assert task.total_elements == 0


@pytest.mark.asyncio
async def test_query_task_pagination():
    """Test QueryTask with pagination parameters."""
    def get_fruits(query: str) -> list[str]:
        query = query.lower()
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    executor = MockTaskExecutor()

    # Test max_elements limit
    task = QueryTask(search_fn=get_fruits, query="berry", max_elements=1)
    executor.schedule(task)
    await executor._execute_current_task()
    assert len(task.elements) == 1
    assert task.elements == ["Blackberry"]
    assert task.total_elements == 3  # Total matches (Blackberry, Blueberry, Cranberry)
    assert task.more_elements  # Indicates there are more results

    # Test first_element_index
    task = QueryTask(search_fn=get_fruits, query="berry", first_element_index=1)
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Blueberry", "Cranberry"]
    assert task.first_element_index == 1


@pytest.mark.asyncio
async def test_query_task_cancellation():
    """Test QueryTask cancellation."""
    def slow_search(query: str) -> list[str]:
        if query == "cancel_me":
            return []  # Should never get here due to cancellation
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    executor = MockTaskExecutor()

    # Test normal execution
    task = QueryTask(search_fn=slow_search, query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Apple"]

    # Test cancellation
    task = QueryTask(search_fn=slow_search, query="cancel_me")
    executor.schedule(task)
    executor.cancel()
    assert task.is_cancelled
    assert not task.elements


@pytest.mark.asyncio
async def test_query_task_error_handling():
    """Test QueryTask error handling."""
    def failing_search(query: str) -> list[str]:
        raise ValueError("Search failed")

    executor = MockTaskExecutor()
    task = QueryTask(search_fn=failing_search, query="test")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert task.has_error
    assert isinstance(task.error, ValueError)
    assert str(task.error) == "Search failed"
    assert task.elements == []


@pytest.mark.asyncio
async def test_query_task_empty_query():
    """Test QueryTask with empty query."""
    def search_fn(query: str) -> list[str]:
        if not query:
            return FRUITS
        return [fruit for fruit in FRUITS if query.lower() in fruit.lower()]

    executor = MockTaskExecutor()

    # Test empty query returns all results
    task = QueryTask(search_fn=search_fn, query="")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == FRUITS
    assert task.total_elements == len(FRUITS)

    # Test None query
    task = QueryTask(search_fn=search_fn, query=None)
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == []  # QueryTask handles None query by not executing search


@pytest.mark.asyncio
async def test_custom_query_task_sync():
    """Test QueryTask with custom execute method."""
    class CustomQueryTask(QueryTask):
        def execute(self):
            if not self._query:
                return
            # Custom implementation that adds a prefix to results
            result = [f"Custom_{fruit}" for fruit in FRUITS if self._query.lower() in fruit.lower()]
            self._total_elements = len(result)
            self.set_elements(result)

    executor = MockTaskExecutor()

    # Test custom execution
    task = CustomQueryTask(query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert not task.has_error
    assert task.elements == ["Custom_Apple"]
    assert task.total_elements == 1

    # Test with pagination
    task = CustomQueryTask(query="berry", max_elements=2)
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Custom_Blackberry", "Custom_Blueberry"]
    assert task.total_elements == 3
    assert task.more_elements


@pytest.mark.asyncio
async def test_custom_query_task_async():
    """Test QueryTask with custom execute_async method."""
    class CustomAsyncQueryTask(QueryTask):
        async def execute_async(self):
            if not self._query:
                return
            # Custom implementation that adds a prefix to results
            result = [f"Async_{fruit}" for fruit in FRUITS if self._query.lower() in fruit.lower()]
            self._total_elements = len(result)
            self.set_elements(result)

    executor = MockTaskExecutor()

    # Test custom async execution
    task = CustomAsyncQueryTask(query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert not task.has_error
    assert task.elements == ["Async_Apple"]
    assert task.total_elements == 1

    # Test with pagination
    task = CustomAsyncQueryTask(query="berry", max_elements=2)
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Async_Blackberry", "Async_Blueberry"]
    assert task.total_elements == 3
    assert task.more_elements

    # Test error handling in custom implementation
    class ErrorAsyncQueryTask(QueryTask):
        async def execute_async(self):
            raise ValueError("Custom async error")

    task = ErrorAsyncQueryTask(query="test")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert task.has_error
    assert isinstance(task.error, ValueError)
    assert str(task.error) == "Custom async error"


@pytest.mark.asyncio
async def test_async_callback_with_run():
    """Test using an async callback with run() method."""
    async def async_filter(query: str) -> list[str]:
        query = query.lower()
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    # Test with run() - should raise NotImplementedError
    task = QueryTask(search_fn=async_filter, query="apple")
    with pytest.raises(NotImplementedError, match="Use execute_async for async search functions"):
        task.execute()  # This should trigger the error


@pytest.mark.asyncio
async def test_async_callback_with_run_async():
    """Test using an async callback with run_async() method."""
    async def async_filter(query: str) -> list[str]:
        query = query.lower()
        return [fruit for fruit in FRUITS if query in fruit.lower()]

    executor = MockTaskExecutor()

    # Test with run_async() - should work correctly
    task = QueryTask(search_fn=async_filter, query="apple")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert not task.has_error
    assert task.elements == ["Apple"]

    # Test pagination with async callback
    task = QueryTask(search_fn=async_filter, query="berry", max_elements=2)
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.elements == ["Blackberry", "Blueberry"]
    assert task.total_elements == 3
    assert task.more_elements

    # Test error handling with async callback
    async def failing_async_filter(query: str) -> list[str]:
        raise ValueError("Async filter failed")

    task = QueryTask(search_fn=failing_async_filter, query="test")
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert task.has_error
    assert isinstance(task.error, ValueError)
    assert str(task.error) == "Async filter failed"
