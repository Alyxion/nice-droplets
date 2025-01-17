import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_table_factory import FlexTableFactory
from dataclasses import dataclass

@dataclass
class TestItem:
    name: str
    value: int
    
    def to_dict(self):
        return {'name': self.name, 'value': self.value}

@pytest.fixture
def dict_items():
    """Sample dictionary items for testing."""
    return [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]

@pytest.fixture
def dataclass_items():
    """Sample dataclass items for testing."""
    return [
        TestItem('Item 1', 10),
        TestItem('Item 2', 20),
        TestItem('Item 3', 30)
    ]

@pytest.fixture
def columns():
    """Sample column definitions."""
    return [
        {'name': 'name', 'label': 'Name', 'field': 'name'},
        {'name': 'value', 'label': 'Value', 'field': 'value'}
    ]

def test_table_factory_initialization(screen: Screen):
    """Test factory initialization with and without columns."""
    # Test without columns
    factory = FlexTableFactory()
    screen.open('/')
    assert factory._columns is None
    
    # Test with string columns
    string_columns = ['name', 'value']
    factory = FlexTableFactory(columns=string_columns)
    screen.open('/')
    assert factory._columns == string_columns
    
    # Test with dict columns
    dict_columns = [{'name': 'name', 'label': 'Name', 'field': 'name'}]
    factory = FlexTableFactory(columns=dict_columns)
    screen.open('/')
    assert factory._columns == dict_columns

def test_table_factory_with_dict_items(screen: Screen, dict_items):
    """Test table creation with dictionary items."""
    factory = FlexTableFactory()
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert factory._table is not None
    assert len(factory._items) == 3
    assert all('_index' in row for row in factory._table.rows)

def test_table_factory_with_dataclass_items(screen: Screen, dataclass_items):
    """Test table creation with dataclass items."""
    factory = FlexTableFactory()
    factory.create_container()
    screen.open('/')
    factory.update_items(dataclass_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    assert factory._table is not None
    assert len(factory._items) == 3
    # Check if items were properly converted to dicts
    assert all(isinstance(row, dict) for row in factory._table.rows)

def test_table_factory_with_string_columns(screen: Screen):
    """Test table creation with string column definitions."""
    columns = ['name', 'value']
    factory = FlexTableFactory(columns=columns)
    factory.create_container()
    screen.open('/')
    items = [{'name': 'Test', 'value': 1}]
    factory.update_items(items)
    
    screen.should_contain('Test')
    screen.should_contain('1')
    table_columns = factory._table.columns
    assert len(table_columns) == 2
    assert table_columns[0]['label'] == 'Name'  # Should be title case
    assert table_columns[1]['label'] == 'Value'

def test_table_factory_with_dict_columns(screen: Screen, columns, dict_items):
    """Test table creation with dictionary column definitions."""
    factory = FlexTableFactory(columns=columns)
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')
    table_columns = factory._table.columns
    assert len(table_columns) == 2
    assert table_columns[0]['label'] == 'Name'
    assert table_columns[1]['label'] == 'Value'

def test_table_factory_selection(screen: Screen, dict_items):
    """Test selection handling in table."""
    factory = FlexTableFactory()
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    # Test selection
    factory.index = 1
    screen.wait(0.1)  # Wait for selection update
    assert factory._table.selected == [dict_items[1]]
    
    # Test deselection
    factory.index = -1
    screen.wait(0.1)  # Wait for selection update
    assert factory._table.selected == []

def test_table_factory_row_click(screen: Screen, dict_items):
    """Test row click handling."""
    clicked_item = None
    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item
    
    factory = FlexTableFactory(on_item_click=on_click)
    factory.create_container()
    screen.open('/')
    factory.update_items(dict_items)
    
    # Simulate row click by directly calling handle_item_click
    factory.handle_item_click(1)
    screen.wait(0.1)  # Wait for click handling
    assert clicked_item == dict_items[1]

def test_table_factory_clear(screen: Screen):
    """Test clearing table."""
    factory = FlexTableFactory()
    factory.create_container()
    screen.open('/')
    factory.update_items([{'name': 'Test'}])
    
    screen.should_contain('Test')
    assert factory._table is not None
    
    factory.clear()
    screen.wait(0.1)  # Wait for UI update
    screen.should_not_contain('Test')
    assert factory._table is None
    assert len(factory._items) == 0

def test_table_factory_item_to_dict_error(screen: Screen):
    """Test error handling for invalid item types."""
    factory = FlexTableFactory()
    screen.open('/')
    
    with pytest.raises(TypeError):
        factory.item_to_dict("invalid item")  # String can't be converted to dict

def test_table_factory_empty_items(screen: Screen):
    """Test handling empty items list."""
    factory = FlexTableFactory()
    factory.create_container()
    screen.open('/')
    factory.update_items([])
    
    assert factory._table is None
    assert len(factory._items) == 0

def test_table_factory_disabled_items(screen: Screen, dict_items):
    """Test handling disabled items."""
    disabled_items = [
        {'name': 'Item 1', 'value': 10, 'disabled': True},
        {'name': 'Item 2', 'value': 20}
    ]
    
    clicked_items = []
    def on_click(e):
        clicked_items.append(e.item)
    
    factory = FlexTableFactory(on_item_click=on_click)
    factory.create_container()
    screen.open('/')
    factory.update_items(disabled_items)
    
    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    
    # Simulate clicks by directly calling handle_item_click
    factory.handle_item_click(0)  # Click disabled row
    factory.handle_item_click(1)  # Click enabled row
    screen.wait(0.1)  # Wait for click handling
    
    assert len(clicked_items) == 2  # Both clicks should register in this implementation
    assert clicked_items[0] == disabled_items[0]
    assert clicked_items[1] == disabled_items[1]
