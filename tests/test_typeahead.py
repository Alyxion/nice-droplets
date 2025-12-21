import pytest
from nicegui import ui, run, app
from nicegui.testing import Screen
from nice_droplets import dui
from nice_droplets.tasks.query_task import QueryTask

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
    refs = []

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead()
        typeahead.observe(input_field)
        refs.append(typeahead)

    screen.open('/')
    screen.wait(0.3)

    typeahead = refs[0]
    assert typeahead._min_chars == 1
    assert typeahead._search_list._search_manager._task_executor._debounce == 0.1


def test_typeahead_search(screen: Screen):
    """Test Typeahead search functionality."""
    refs = []

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead(
            on_search=lambda query: QueryTask(search_items, query)
        )
        typeahead.observe(input_field)
        refs.append((input_field, typeahead))

    screen.open('/')
    screen.wait(0.3)

    input_field, typeahead = refs[0]
    typeahead.show_at(input_field)
    input_field.run_method('focus')
    input_field.set_value('ap')
    screen.wait(0.3)

    screen.should_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')


def test_typeahead_min_chars(screen: Screen):
    """Test Typeahead minimum characters requirement."""
    refs = []

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead(
            on_search=lambda query: QueryTask(search_items, query),
            min_chars=2
        )
        typeahead.observe(input_field)
        refs.append((input_field, typeahead))

    screen.open('/')
    screen.wait(0.3)

    input_field, typeahead = refs[0]
    typeahead.show_at(input_field)
    input_field.set_value('a')
    screen.wait(0.3)

    screen.should_not_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')

    input_field.set_value('ap')
    screen.wait(0.3)

    screen.should_contain('Apple')
    screen.should_not_contain('Banana')
    screen.should_not_contain('Cherry')


def test_typeahead_factory_tuple_basic(screen: Screen):
    """Test Typeahead with factory passed as tuple with parameters."""
    refs = []
    clicked_item = None

    def on_item_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead(
            on_search=lambda query: QueryTask(search_items, query),
            factory=('Item', {'on_item_click': on_item_click})
        )
        typeahead.observe(input_field)
        refs.append((input_field, typeahead))

    screen.open('/')
    screen.wait(0.3)

    input_field, typeahead = refs[0]
    typeahead.show_at(input_field)
    input_field.set_value('ap')
    screen.wait(0.3)

    screen.should_contain('Apple')

    typeahead._search_list._view_factory.handle_item_click(0)
    assert clicked_item == 'Apple'


def test_typeahead_factory_tuple_table(screen: Screen):
    """Test Typeahead with table factory passed as tuple with parameters."""
    refs = []
    clicked_item = None

    def on_item_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead(
            on_search=lambda query: QueryTask(lambda q: [{"name": "Apple", "type": "fruit"}], query),
            factory=('Table', {
                'on_item_click': on_item_click,
                'columns': [
                    {'name': 'name', 'label': 'Name', 'field': 'name'},
                    {'name': 'type', 'label': 'Type', 'field': 'type'}
                ]
            })
        )
        typeahead.observe(input_field)
        refs.append((input_field, typeahead))

    screen.open('/')
    screen.wait(0.3)

    input_field, typeahead = refs[0]
    typeahead.show_at(input_field)
    input_field.set_value('ap')
    screen.wait(0.3)

    screen.should_contain('Name')
    screen.should_contain('Type')

    typeahead._search_list._view_factory.handle_item_click(0)
    assert clicked_item == {"name": "Apple", "type": "fruit"}


def test_typeahead_show_hide_events(screen: Screen):
    """Test Typeahead show/hide events."""
    refs = []
    show_count = 0
    hide_count = 0

    def on_show(e):
        nonlocal show_count
        show_count += 1

    def on_hide(e):
        nonlocal hide_count
        hide_count += 1

    @ui.page('/')
    def page():
        input_field = ui.input()
        typeahead = dui.typeahead(
            on_search=lambda query: QueryTask(search_items, query),
            min_chars=2,
            on_show=on_show,
            on_hide=on_hide
        )
        typeahead.observe(input_field)
        refs.append((input_field, typeahead))

    screen.open('/')
    screen.wait(0.3)

    input_field, typeahead = refs[0]
    input_field.set_value('app')
    screen.wait(0.3)
    typeahead.show_at(input_field)
    screen.wait(0.3)

    assert show_count == 1
    assert hide_count == 0

    typeahead.hide()
    screen.wait(0.3)

    assert show_count == 1
    assert hide_count == 1
