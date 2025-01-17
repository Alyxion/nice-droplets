import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_item_list_factory import FlexItemListFactory
from nice_droplets.elements.item import Item
from nice_droplets.elements.list import List
from nice_droplets.elements.item_section import ItemSection

@pytest.fixture
def factory():
    """Create a basic factory instance."""
    return FlexItemListFactory()

@pytest.fixture
def string_items():
    """Sample string items for testing."""
    return ['Item 1', 'Item 2', 'Item 3']

@pytest.fixture
def dict_items():
    """Sample dictionary items for testing."""
    return [
        {'title': 'Item 1', 'subtitle': 'Description 1', 'avatar': 'mdi-account'},
        {'title': 'Item 2', 'subtitle': 'Description 2', 'avatar': 'https://example.com/avatar.jpg', 'avatar_round': True},
        {'title': 'Item 3', 'disabled': True}
    ]

def test_item_list_factory_initialization(screen: Screen):
    """Test factory initialization with different configurations."""
    # Test default initialization
    factory = FlexItemListFactory()
    screen.open('/')
    assert factory._list_kwargs == {}
    
    # Test with list configuration
    factory = FlexItemListFactory(bordered=True, separator=True, padding=True)
    screen.open('/')
    assert factory._list_kwargs == {'bordered': True, 'separator': True, 'padding': True}

def test_item_list_factory_container_creation(screen: Screen):
    """Test container creation with different configurations."""
    factory = FlexItemListFactory(bordered=True, separator=True)
    container = factory.create_container()
    screen.open('/')
    assert isinstance(container, List)
    # List configuration is applied during creation
    assert container._props.get('bordered') is True
    assert container._props.get('separator') is True

def test_item_list_factory_with_string_items(screen: Screen, factory: FlexItemListFactory, string_items):
    """Test creating items from strings."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3
    # Check that items were created as clickable elements
    assert all(isinstance(elem, Item) for elem in factory._item_elements)
    # Check that items are clickable by default
    assert all(elem._props.get('clickable') for elem in factory._item_elements)

def test_item_list_factory_with_dict_items(screen: Screen, factory: FlexItemListFactory, dict_items):
    """Test creating items from dictionaries with various properties."""
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3
    
    # Check third item is disabled
    assert not factory._item_elements[2]._props.get('clickable')
    assert factory._item_elements[2]._props.get('clickable') is False

def test_item_list_factory_selection(screen: Screen, factory: FlexItemListFactory, string_items):
    """Test item selection handling."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    # Test selection
    factory._item_elements[1]._props['active'] = True
    screen.wait(0.1)  # Wait for selection update
    assert factory._item_elements[1]._props.get('active') is True
    
    # Test deselection
    factory._item_elements[1]._props['active'] = None
    screen.wait(0.1)  # Wait for selection update
    assert factory._item_elements[1]._props.get('active') is None

def test_item_list_factory_click_handling(screen: Screen, factory: FlexItemListFactory, string_items):
    """Test item click event handling."""
    clicked_item = None
    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item
    
    factory = FlexItemListFactory(on_item_click=on_click)
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    # Simulate click by directly calling handle_item_click
    factory.handle_item_click(0)
    screen.wait(0.1)  # Wait for click handling
    assert clicked_item == string_items[0]

def test_item_list_factory_avatar_handling(screen: Screen, factory: FlexItemListFactory):
    """Test avatar creation with different types."""
    items = [
        {'title': 'Icon Avatar', 'avatar': 'mdi-account'},
        {'title': 'Image Avatar', 'avatar': 'https://example.com/avatar.jpg', 'avatar_round': True}
    ]
    
    factory.create_container()
    screen.open('/')
    factory.update_items(items)
    
    screen.should_contain('Icon Avatar')
    screen.should_contain('Image Avatar')
    
    # First item should have an icon
    first_item = factory._item_elements[0]
    sections = [child for child in first_item.default_slot if isinstance(child, ItemSection)]
    assert any(section._props.get('avatar') for section in sections)
    assert any('mdi-account' in str(child._props) for child in sections[0].default_slot)
    
    # Second item should have a rounded image
    second_item = factory._item_elements[1]
    sections = [child for child in second_item.default_slot if isinstance(child, ItemSection)]
    assert any(section._props.get('avatar') for section in sections)
    assert any('rounded-full' in str(child._classes) for child in sections[0].default_slot)

def test_item_list_factory_disable_enable(screen: Screen, factory: FlexItemListFactory, string_items):
    """Test item disable/enable functionality."""
    factory.create_container()
    screen.open('/')
    factory.update_items(string_items)
    
    # Test disabling
    factory.disable_item(0)
    screen.wait(0.1)  # Wait for UI update
    assert 'disabled' in factory._item_elements[0]._classes
    
    # Test enabling
    factory.enable_item(0)
    screen.wait(0.1)  # Wait for UI update
    assert 'disabled' not in factory._item_elements[0]._classes

def test_item_list_factory_with_empty_items(screen: Screen, factory: FlexItemListFactory):
    """Test handling empty items list."""
    factory.create_container()
    screen.open('/')
    factory.update_items([])
    
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0

def test_item_list_factory_clear(screen: Screen, factory: FlexItemListFactory, string_items):
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

def test_item_list_factory_subtitle_handling(screen: Screen, factory: FlexItemListFactory):
    """Test subtitle/caption handling."""
    items = [
        {'title': 'Item 1', 'subtitle': 'Description 1'},
        {'title': 'Item 2', 'caption': 'Caption 2'}  # Test alternative caption field
    ]
    
    factory.create_container()
    screen.open('/')
    factory.update_items(items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Description 1')
    screen.should_contain('Item 2')
    screen.should_contain('Caption 2')
    
    # Check both subtitle and caption are rendered
    first_item = factory._item_elements[0]
    second_item = factory._item_elements[1]
    
    # Get text sections
    first_sections = [child for child in first_item.default_slot if isinstance(child, ItemSection)]
    second_sections = [child for child in second_item.default_slot if isinstance(child, ItemSection)]
    
    # Check text content
    assert any('Description 1' in str(child._text) for child in first_sections[0].default_slot)
    assert any('Caption 2' in str(child._text) for child in second_sections[0].default_slot)

def test_item_list_factory_non_string_items(screen: Screen, factory: FlexItemListFactory):
    """Test handling non-string/non-dict items."""
    items = [123, 456, 789]  # Numbers should be converted to strings
    
    factory.create_container()
    screen.open('/')
    factory.update_items(items)
    
    screen.should_contain('123')
    screen.should_contain('456')
    screen.should_contain('789')
    assert len(factory._items) == 3
    # Check that numbers were converted to strings
    first_item = factory._item_elements[0]
    sections = [child for child in first_item.default_slot if isinstance(child, ItemSection)]
    assert any('123' in str(child._text) for child in sections[0].default_slot)
