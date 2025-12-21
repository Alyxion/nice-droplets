import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets import dui


def test_flex_list_initialization(screen: Screen):
    """Test FlexList initialization with default parameters."""
    flex_list_ref = []

    @ui.page('/')
    def page():
        flex_list = dui.flex_list()
        flex_list_ref.append(flex_list)

    screen.open('/')
    screen.wait(0.3)

    assert flex_list_ref[0].items == []


def test_flex_list_with_items(screen: Screen):
    """Test FlexList initialization with items."""
    items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        dui.flex_list(items=items)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')


def test_flex_list_set_items(screen: Screen):
    """Test setting items after initialization."""
    items = ['Item 1', 'Item 2', 'Item 3']
    flex_list_ref = []

    @ui.page('/')
    def page():
        flex_list = dui.flex_list()
        flex_list_ref.append(flex_list)

    screen.open('/')
    screen.wait(0.3)

    flex_list_ref[0].items = items
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')


def test_flex_list_clear_items(screen: Screen):
    """Test clearing items."""
    items = ['Item 1', 'Item 2', 'Item 3']
    flex_list_ref = []

    @ui.page('/')
    def page():
        flex_list = dui.flex_list(items=items)
        flex_list_ref.append(flex_list)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    flex_list_ref[0].items = []
    screen.wait(0.3)

    screen.should_not_contain('Item 1')
    screen.should_not_contain('Item 2')
    screen.should_not_contain('Item 3')


def test_flex_list_content_update_event(screen: Screen):
    """Test content update event is fired when items change."""
    items = ['Item 1', 'Item 2', 'Item 3']
    received_items = None
    flex_list_ref = []

    def on_content_update(e):
        nonlocal received_items
        received_items = e.items

    @ui.page('/')
    def page():
        flex_list = dui.flex_list(on_content_update=on_content_update)
        flex_list_ref.append(flex_list)

    screen.open('/')
    screen.wait(0.3)

    flex_list_ref[0].items = items
    screen.wait(0.3)

    assert received_items == items


def test_flex_list_click_event(screen: Screen):
    """Test item click event."""
    items = ['Item 1', 'Item 2', 'Item 3']
    clicked_item = None

    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        dui.flex_list(items=items, on_click=on_click)

    screen.open('/')
    screen.wait(0.3)

    screen.click('Item 1')
    screen.wait(0.3)

    assert clicked_item == 'Item 1'


def test_flex_list_keyboard_navigation(screen: Screen):
    """Test keyboard navigation."""
    items = ['Item 1', 'Item 2', 'Item 3']
    clicked_item = None
    flex_list_ref = []

    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        flex_list = dui.flex_list(items=items, on_click=on_click)
        flex_list_ref.append(flex_list)

    screen.open('/')
    screen.wait(0.3)

    flex_list = flex_list_ref[0]

    # Create mock event arguments
    class MockEventArguments:
        def __init__(self, key: str):
            self.args = {'key': key}

    # Move down with arrow keys
    flex_list._handle_key(MockEventArguments('ArrowDown'))
    screen.wait(0.1)
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 1'

    # Move down again
    flex_list._handle_key(MockEventArguments('ArrowDown'))
    screen.wait(0.1)
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 2'

    # Move up
    flex_list._handle_key(MockEventArguments('ArrowUp'))
    screen.wait(0.1)
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 1'

    # Clear selection with escape
    flex_list._handle_key(MockEventArguments('Escape'))
    assert flex_list._view_factory.index == -1
