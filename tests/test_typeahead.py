import pytest
from nicegui import ui, run, app
from nicegui.testing import Screen
from nice_droplets.elements.typeahead import Typeahead
from nice_droplets.components import SearchTask

ITEMS = [
    'Apple', 'Banana', 'Cherry',
    'Date', 'Elderberry', 'Fig',
    'Grape', 'Honeydew'
]


def search_items(query: str) -> list[str]:
    """Search items that match the query."""
    query = query.lower()
    return [item for item in ITEMS if query in item.lower()]


def test_typeahead_initialization(screen: Screen):
    """Test Typeahead initialization with default parameters."""
    with ui.element():
        input_field = ui.input()
        typeahead = Typeahead()
        typeahead.observe(input_field)

    screen.open('/')
    assert typeahead._min_chars == 1
    assert typeahead._search_list._search_manager._task_executor._debounce == 0.1


def test_typeahead_search(screen: Screen):
    """Test Typeahead search functionality."""
    with ui.element():
        input_field = ui.input()
        typeahead = Typeahead(
            on_search=lambda query: SearchTask(search_items, query)
        )
        typeahead.observe(input_field)

    screen.open('/')

    typeahead.show_at(input_field)  # manually focus, focussing events do not trigger
    # Focus input and type search query
    input_field.run_method('focus')
    input_field.set_value('ap')
    screen.wait(0.5)  # Wait for search

    # Verify results are displayed
    screen.should_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')


def test_typeahead_min_chars(screen: Screen):
    """Test Typeahead minimum characters requirement."""
    with ui.element():
        input_field = ui.input()
        typeahead = Typeahead(
            on_search=lambda query: SearchTask(search_items, query),
            min_chars=2
        )
        typeahead.observe(input_field)

    screen.open('/')

    # Focus input and type single character
    typeahead.show_at(input_field)
    input_field.set_value('a')
    screen.wait(0.5)  # Wait for search

    # Verify no results are displayed
    screen.should_not_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')

    # Type second character
    input_field.set_value('ap')
    screen.wait(0.5)  # Wait for search

    # Verify results are displayed
    screen.should_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')

# test on_show and on_hide events
def test_typeahead_show_hide_events(screen: Screen):
    with ui.element():
        input_field = ui.input()
        show_count = 0
        hide_count = 0

        def on_show(e):
            nonlocal show_count
            show_count += 1

        def on_hide(e):
            nonlocal hide_count
            hide_count += 1

        typeahead = Typeahead(
            on_search=lambda query: SearchTask(search_items, query),
            min_chars=2,
            on_show=on_show,
            on_hide=on_hide
        )
        typeahead.observe(input_field)

    screen.open('/')

    # Focus input and type single character
    input_field.set_value('app')
    screen.wait(0.5)
    typeahead.show_at(input_field)
    screen.wait(0.5)

    assert show_count == 1
    assert hide_count == 0

    typeahead.hide()
    screen.wait(0.5)

    assert show_count == 1
    assert hide_count == 1