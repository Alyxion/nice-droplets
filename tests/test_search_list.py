import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets import dui
from nice_droplets.tasks.query_task import QueryTask


def test_search_list_initialization(screen: Screen):
    """Test SearchList initialization with default parameters."""
    refs = []

    @ui.page('/')
    def page():
        search_list = dui.search_list()
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    assert search_list.items == []
    assert search_list._search_manager._min_chars == 1
    assert search_list._search_manager._task_executor._debounce == 0.3
    assert search_list._search_manager._poll_interval == 0.1


def test_search_list_custom_params(screen: Screen):
    """Test SearchList initialization with custom parameters."""
    refs = []

    @ui.page('/')
    def page():
        search_list = dui.search_list(min_chars=2, debounce=0.5, poll_interval=0.2)
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    assert search_list._search_manager._min_chars == 2
    assert search_list._search_manager._task_executor._debounce == 0.5
    assert search_list._search_manager._poll_interval == 0.2


def test_set_search_query_below_min_chars(screen: Screen):
    """Test setting search query below minimum characters."""
    refs = []

    @ui.page('/')
    def page():
        search_list = dui.search_list(min_chars=2)
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    search_list.set_search_query('a')
    assert search_list.items == []


def test_search_error_handling(screen: Screen):
    """Test handling of search errors."""
    refs = []

    @ui.page('/')
    def page():
        search_list = dui.search_list()
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    search_list.items = ['Initial item']
    search_list.on_search_error(Exception('Search failed'))
    assert search_list.items == []


def test_search_results_handling(screen: Screen):
    """Test handling of search results."""
    refs = []
    search_results = ['Result 1', 'Result 2', 'Result 3']

    @ui.page('/')
    def page():
        search_list = dui.search_list()
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    search_list.on_search_results(search_results)
    screen.wait(0.3)

    screen.should_contain('Result 1')
    screen.should_contain('Result 2')
    screen.should_contain('Result 3')


def test_content_update_event(screen: Screen):
    """Test content update event is fired when results are received."""
    refs = []
    received_items = None
    search_results = ['Result 1', 'Result 2', 'Result 3']

    def on_content_update(e):
        nonlocal received_items
        received_items = e.items

    @ui.page('/')
    def page():
        search_list = dui.search_list(on_content_update=on_content_update)
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    search_list.on_search_results(search_results)
    assert received_items == search_results


def test_search_with_callback(screen: Screen):
    """Test search with callback function."""
    refs = []
    search_results = ['Result 1', 'Result 2', 'Result 3']

    async def search_func():
        return search_results

    def search_callback(query: str) -> QueryTask:
        return QueryTask(search_func)

    @ui.page('/')
    def page():
        search_list = dui.search_list(on_search=search_callback)
        refs.append(search_list)

    screen.open('/')
    screen.wait(0.3)

    search_list = refs[0]
    search_list.on_search_results(search_results)
    screen.wait(0.3)

    screen.should_contain('Result 1')
    screen.should_contain('Result 2')
    screen.should_contain('Result 3')
