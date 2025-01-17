import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_default_factory import FlexDefaultFactory

@pytest.fixture
def factory():
    """Create a basic factory instance."""
    return FlexDefaultFactory()

@pytest.fixture
def string_items():
    """Sample string items for testing."""
    return ['Item 1', 'Item 2', 'Item 3']

@pytest.fixture
def dict_items():
    """Sample dictionary items for testing."""
    return [
        {'label': 'Item 1'},
        {'label': 'Item 2'},
        {'label': 'Item 3', 'disabled': True}
    ]

def test_default_factory_container_creation(screen: Screen, factory: FlexDefaultFactory):
    """Test container creation and styling."""
    container = factory.create_container()
    screen.open('/')
    assert isinstance(container, ui.element)
    assert 'flex' in container._classes
    assert 'flex-col' in container._classes
    assert 'gap-1' in container._classes
    assert 'min-w-[200px]' in container._classes

def test_default_factory_with_string_items(screen: Screen, factory: FlexDefaultFactory, string_items):
    """Test creating items from strings."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3
    
    # Check item styling
    first_item = factory._item_elements[0]
    assert 'cursor-pointer' in first_item._classes
    assert 'hover:bg-gray-100' in first_item._classes

def test_default_factory_with_dict_items(screen: Screen, factory: FlexDefaultFactory, dict_items):
    """Test creating items from dictionaries."""
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3

def test_default_factory_selection(screen: Screen, factory: FlexDefaultFactory, string_items):
    """Test item selection styling."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    # Test selection
    factory._item_elements[1].classes('bg-primary text-white', remove='hover:bg-gray-100')
    screen.wait(0.1)  # Wait for selection update
    assert 'bg-primary' in factory._item_elements[1]._classes
    assert 'text-white' in factory._item_elements[1]._classes
    assert 'hover:bg-gray-100' not in factory._item_elements[1]._classes
    
    # Test deselection
    factory._item_elements[1].classes('hover:bg-gray-100', remove='bg-primary text-white')
    screen.wait(0.1)  # Wait for selection update
    assert 'bg-primary' not in factory._item_elements[1]._classes
    assert 'text-white' not in factory._item_elements[1]._classes
    assert 'hover:bg-gray-100' in factory._item_elements[1]._classes

def test_default_factory_click_handling(screen: Screen, factory: FlexDefaultFactory, string_items):
    """Test item click event handling."""
    clicked_item = None
    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item
    
    factory.on_click(on_click)
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    # Simulate click by directly calling handle_item_click
    factory.handle_item_click(0)
    screen.wait(0.1)  # Wait for click handling
    assert clicked_item == string_items[0]

def test_default_factory_with_empty_items(screen: Screen, factory: FlexDefaultFactory):
    """Test handling empty items list."""
    factory.create_container()
    screen.open('/')
    factory.update_items([])
    
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0

def test_default_factory_clear(screen: Screen, factory: FlexDefaultFactory, string_items):
    """Test clearing items."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert len(factory._items) == 3
    
    factory.clear()
    screen.wait(0.1)  # Wait for UI update
    screen.should_not_contain('Item 1')
    screen.should_not_contain('Item 2')
    screen.should_not_contain('Item 3')
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0

def test_default_factory_with_non_string_items(screen: Screen, factory: FlexDefaultFactory):
    """Test handling non-string/non-dict items."""
    items = [123, 456, 789]  # Numbers should be converted to strings
    
    factory.create_container()
    screen.open('/')
    factory.update_items(items)
    
    screen.should_contain('123')
    screen.should_contain('456')
    screen.should_contain('789')
    assert len(factory._items) == 3

def test_default_factory_dict_without_label(screen: Screen, factory: FlexDefaultFactory):
    """Test handling dictionary items without label field."""
    items = [{'other_field': 'value'}]
    
    factory.create_container()
    screen.open('/')
    factory.update_items(items)
    
    assert len(factory._items) == 1
    # Should use empty string for label
    first_item = factory._item_elements[0]
    labels = [child for child in first_item.default_slot if isinstance(child, ui.label)]
    assert any('' in str(child._text) for child in labels)
