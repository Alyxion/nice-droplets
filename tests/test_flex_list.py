import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.elements.flex_list import FlexList

@pytest.fixture
def items() -> list[str]:
    """Sample items for testing."""
    return ['Item 1', 'Item 2', 'Item 3']

def test_flex_list_initialization(screen: Screen):
    """Test FlexList initialization with default parameters."""
    flex_list = FlexList()
    screen.open('/')
    assert flex_list.items == []

def test_flex_list_with_items(screen: Screen, items):
    """Test FlexList initialization with items."""
    flex_list = FlexList(items=items)
    screen.open('/')
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

def test_flex_list_set_items(screen: Screen, items):
    """Test setting items after initialization."""
    flex_list = FlexList()
    screen.open('/')
    flex_list.items = items
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

def test_flex_list_clear_items(screen: Screen, items):
    """Test clearing items."""
    flex_list = FlexList(items=items)
    screen.open('/')
    # Verify items are visible first
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    
    flex_list.items = []  # Set items to empty list to clear
    screen.wait(0.5)  # Wait for UI update
    screen.should_not_contain('Item 1')
    screen.should_not_contain('Item 2')
    screen.should_not_contain('Item 3')

def test_flex_list_content_update_event(screen: Screen, items):
    """Test content update event is fired when items change."""
    received_items = None
    
    def on_content_update(e):
        nonlocal received_items
        received_items = e.items
    
    flex_list = FlexList(on_content_update=on_content_update)
    screen.open('/')
    flex_list.items = items
    assert received_items == items

def test_flex_list_click_event(screen: Screen, items):
    """Test item click event."""
    clicked_item = None
    
    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item
    
    flex_list = FlexList(items=items, on_click=on_click)
    screen.open('/')
    screen.click('Item 1')
    assert clicked_item == 'Item 1'

def test_flex_list_keyboard_navigation(screen: Screen, items):
    """Test keyboard navigation."""
    clicked_item = None
    
    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item
    
    with ui.element():
        flex_list = FlexList(items=items, on_click=on_click)
    
    screen.open('/')
    
    # Create mock event arguments
    class MockEventArguments:
        def __init__(self, key: str):
            self.args = {'key': key}
    
    # Move down with arrow keys
    flex_list._handle_key(MockEventArguments('ArrowDown'))
    screen.wait(0.1)  # Wait for selection update
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 1'
    
    # Move down again
    flex_list._handle_key(MockEventArguments('ArrowDown'))
    screen.wait(0.1)  # Wait for selection update
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 2'
    
    # Move up
    flex_list._handle_key(MockEventArguments('ArrowUp'))
    screen.wait(0.1)  # Wait for selection update
    flex_list._handle_key(MockEventArguments('Enter'))
    assert clicked_item == 'Item 1'
    
    # Clear selection with escape
    flex_list._handle_key(MockEventArguments('Escape'))
    assert flex_list._view_factory.index == -1
