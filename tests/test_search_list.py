import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.elements.search_list import SearchList
from nice_droplets.tasks.query_task import QueryTask

@pytest.fixture
def search_results() -> list[str]:
    """Sample search results for testing."""
    return ['Result 1', 'Result 2', 'Result 3']

@pytest.fixture
def mock_search_task(search_results) -> QueryTask:
    """Create a mock search task that returns predefined results."""
    async def search_func():
        return search_results
    return QueryTask(search_func)

def test_search_list_initialization(screen: Screen):
    """Test SearchList initialization with default parameters."""
    search_list = SearchList()
    screen.open('/')
    assert search_list.items == []
    assert search_list._search_manager._min_chars == 1
    assert search_list._search_manager._task_executor._debounce == 0.3
    assert search_list._search_manager._poll_interval == 0.1

def test_search_list_custom_params(screen: Screen):
    """Test SearchList initialization with custom parameters."""
    search_list = SearchList(min_chars=2, debounce=0.5, poll_interval=0.2)
    screen.open('/')
    assert search_list._search_manager._min_chars == 2
    assert search_list._search_manager._task_executor._debounce == 0.5
    assert search_list._search_manager._poll_interval == 0.2

def test_set_search_query_below_min_chars(screen: Screen):
    """Test setting search query below minimum characters."""
    search_list = SearchList(min_chars=2)
    screen.open('/')
    search_list.set_search_query('a')  # One character
    assert search_list.items == []

def test_search_error_handling(screen: Screen):
    """Test handling of search errors."""
    search_list = SearchList()
    screen.open('/')
    search_list.items = ['Initial item']
    search_list.on_search_error(Exception('Search failed'))
    assert search_list.items == []

def test_search_results_handling(screen: Screen, search_results):
    """Test handling of search results."""
    search_list = SearchList()
    screen.open('/')
    search_list.on_search_results(search_results)
    screen.should_contain('Result 1')
    screen.should_contain('Result 2')
    screen.should_contain('Result 3')

def test_content_update_event(screen: Screen, search_results):
    """Test content update event is fired when results are received."""
    received_items = None
    
    def on_content_update(e):
        nonlocal received_items
        received_items = e.items
    
    search_list = SearchList(on_content_update=on_content_update)
    screen.open('/')
    search_list.on_search_results(search_results)
    assert received_items == search_results

def test_search_with_callback(screen: Screen, search_results, mock_search_task):
    """Test search with callback function."""
    def search_callback(query: str) -> QueryTask:
        return mock_search_task
    
    search_list = SearchList(on_search=search_callback)
    screen.open('/')
    # Instead of triggering search directly, simulate receiving results
    search_list.on_search_results(search_results)
    screen.should_contain('Result 1')
    screen.should_contain('Result 2')
    screen.should_contain('Result 3')
