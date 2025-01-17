import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_list_factory import FlexListFactory
from nice_droplets.events import FlexFactoryItemClickedArguments

class SampleFlexListFactory(FlexListFactory):
    """Test implementation of FlexListFactory with required methods implemented."""
    def create_container(self) -> ui.element:
        self._container = ui.element('div')
        return self._container
    
    def create_item(self, data: any) -> ui.element:
        elem = ui.element('div')
        elem._text = str(data)
        return elem
    
    def select_item(self, index: int) -> None:
        if 0 <= index < len(self._item_elements):
            self._item_elements[index]._classes.add('selected')
    
    def deselect_item(self, index: int) -> None:
        if 0 <= index < len(self._item_elements):
            self._item_elements[index]._classes.remove('selected')

@pytest.fixture
def factory():
    """Create a test factory instance."""
    return SampleFlexListFactory()

@pytest.fixture
def items():
    """Sample items for testing."""
    return ['Item 1', 'Item 2', 'Item 3']

def test_factory_initialization():
    """Test factory initialization with and without click handler."""
    # Test without click handler
    factory = SampleFlexListFactory()
    assert factory.index == -1
    assert len(factory._click_handler) == 0

    # Test with click handler
    def on_click(e): pass
    factory = SampleFlexListFactory(on_item_click=on_click)
    assert len(factory._click_handler) == 1

def test_factory_index_management(factory: SampleFlexListFactory):
    """Test index setting and management."""
    factory.index = 1
    assert factory.index == 1
    assert factory._previous_index == -1

    factory.index = 2
    assert factory.index == 2
    assert factory._previous_index == 1

def test_factory_item_click_handling(factory: SampleFlexListFactory, items):
    """Test item click event handling."""
    clicked_data = None
    def on_click(e: FlexFactoryItemClickedArguments):
        nonlocal clicked_data
        clicked_data = e.item

    factory.on_click(on_click)
    factory._container = ui.element('div')
    factory.update_items(items)
    
    # Test clicking first item
    factory.handle_item_click(0)
    assert clicked_data == 'Item 1'

def test_factory_item_state_management(factory: SampleFlexListFactory):
    """Test item enable/disable functionality."""
    items = [
        {'text': 'Item 1', 'disabled': True},
        {'text': 'Item 2', 'disabled': False},
        {'text': 'Item 3'}
    ]
    
    factory._container = ui.element('div')
    factory.update_items(items)
    
    # Check disabled state detection
    assert factory.is_item_disabled(items[0]) is True
    assert factory.is_item_disabled(items[1]) is False
    assert factory.is_item_disabled(items[2]) is False

def test_factory_clear(factory: SampleFlexListFactory, items):
    """Test clearing items."""
    factory._container = ui.element('div')
    factory.update_items(items)
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3
    
    factory.clear()
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0
    assert factory.index == -1
    assert factory._previous_index == -1

def test_factory_update_items(factory: SampleFlexListFactory, items):
    """Test updating items."""
    factory._container = ui.element('div')
    factory.update_items(items)
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3
    
    # Update with new items
    new_items = ['New 1', 'New 2']
    factory.update_items(new_items)
    assert len(factory._items) == 2
    assert len(factory._item_elements) == 2
    assert factory._items == new_items

def test_factory_item_click_with_disabled(factory: SampleFlexListFactory):
    """Test click handling with disabled items."""
    items = [
        {'text': 'Item 1', 'disabled': True},
        {'text': 'Item 2'}
    ]
    
    clicked_items = []
    def on_click(e: FlexFactoryItemClickedArguments):
        clicked_items.append(e.item)
    
    factory.on_click(on_click)
    factory._container = ui.element('div')
    factory.update_items(items)
    
    # Click disabled item
    factory.handle_item_click(0)
    # Click enabled item
    factory.handle_item_click(1)
    
    assert len(clicked_items) == 2  # Both clicks should register in this implementation
    assert clicked_items[0] == items[0]
    assert clicked_items[1] == items[1]
