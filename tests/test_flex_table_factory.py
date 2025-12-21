import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_table_factory import FlexTableFactory
from dataclasses import dataclass


@dataclass
class SampleItem:
    name: str
    value: int

    def to_dict(self):
        return {'name': self.name, 'value': self.value}


def test_table_factory_initialization(screen: Screen):
    """Test factory initialization with and without columns."""
    refs = []

    @ui.page('/')
    def page():
        factory1 = FlexTableFactory()
        string_columns = ['name', 'value']
        factory2 = FlexTableFactory(columns=string_columns)
        dict_columns = [{'name': 'name', 'label': 'Name', 'field': 'name'}]
        factory3 = FlexTableFactory(columns=dict_columns)
        refs.append((factory1, factory2, factory3, string_columns, dict_columns))

    screen.open('/')
    screen.wait(0.3)

    factory1, factory2, factory3, string_columns, dict_columns = refs[0]
    assert factory1._columns is None
    assert factory2._columns == string_columns
    assert factory3._columns == dict_columns


def test_table_factory_with_dict_items(screen: Screen):
    """Test table creation with dictionary items."""
    refs = []
    dict_items = [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        factory.create_container()
        factory.update_items(dict_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = refs[0]
    assert factory._table is not None
    assert len(factory._items) == 3
    assert all('_index' in row for row in factory._table.rows)


def test_table_factory_with_dataclass_items(screen: Screen):
    """Test table creation with dataclass items."""
    refs = []
    dataclass_items = [
        SampleItem('Item 1', 10),
        SampleItem('Item 2', 20),
        SampleItem('Item 3', 30)
    ]

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        factory.create_container()
        factory.update_items(dataclass_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = refs[0]
    assert factory._table is not None
    assert len(factory._items) == 3
    assert all(isinstance(row, dict) for row in factory._table.rows)


def test_table_factory_with_string_columns(screen: Screen):
    """Test table creation with string column definitions."""
    refs = []
    columns = ['name', 'value']
    items = [{'name': 'Test', 'value': 1}]

    @ui.page('/')
    def page():
        factory = FlexTableFactory(columns=columns)
        factory.create_container()
        factory.update_items(items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Test')
    screen.should_contain('1')

    factory = refs[0]
    table_columns = factory._table.columns
    assert len(table_columns) == 2
    assert table_columns[0]['label'] == 'Name'
    assert table_columns[1]['label'] == 'Value'


def test_table_factory_with_dict_columns(screen: Screen):
    """Test table creation with dictionary column definitions."""
    refs = []
    columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name'},
        {'name': 'value', 'label': 'Value', 'field': 'value'}
    ]
    dict_items = [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]

    @ui.page('/')
    def page():
        factory = FlexTableFactory(columns=columns)
        factory.create_container()
        factory.update_items(dict_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = refs[0]
    table_columns = factory._table.columns
    assert len(table_columns) == 2
    assert table_columns[0]['label'] == 'Name'
    assert table_columns[1]['label'] == 'Value'


def test_table_factory_selection(screen: Screen):
    """Test selection handling in table."""
    refs = []
    dict_items = [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        factory.create_container()
        factory.update_items(dict_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = refs[0]
    factory.index = 1
    screen.wait(0.1)
    assert factory._table.selected == [dict_items[1]]

    factory.index = -1
    screen.wait(0.1)
    assert factory._table.selected == []


def test_table_factory_row_click(screen: Screen):
    """Test row click handling."""
    refs = []
    clicked_item = None
    dict_items = [
        {'name': 'Item 1', 'value': 10},
        {'name': 'Item 2', 'value': 20},
        {'name': 'Item 3', 'value': 30}
    ]

    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        factory = FlexTableFactory(on_item_click=on_click)
        factory.create_container()
        factory.update_items(dict_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = refs[0]
    factory.handle_item_click(1)
    screen.wait(0.1)
    assert clicked_item == dict_items[1]


def test_table_factory_clear(screen: Screen):
    """Test clearing table."""
    refs = []

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        factory.create_container()
        factory.update_items([{'name': 'Test'}])
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Test')

    factory = refs[0]
    assert factory._table is not None

    factory.clear()
    screen.wait(0.1)
    screen.should_not_contain('Test')
    assert factory._table is None
    assert len(factory._items) == 0


def test_table_factory_item_to_dict_error(screen: Screen):
    """Test error handling for invalid item types."""
    refs = []

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = refs[0]
    with pytest.raises(TypeError):
        factory.item_to_dict("invalid item")


def test_table_factory_empty_items(screen: Screen):
    """Test handling empty items list."""
    refs = []

    @ui.page('/')
    def page():
        factory = FlexTableFactory()
        factory.create_container()
        factory.update_items([])
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = refs[0]
    assert factory._table is None
    assert len(factory._items) == 0


def test_table_factory_disabled_items(screen: Screen):
    """Test handling disabled items."""
    refs = []
    clicked_items = []
    disabled_items = [
        {'name': 'Item 1', 'value': 10, 'disabled': True},
        {'name': 'Item 2', 'value': 20}
    ]

    def on_click(e):
        clicked_items.append(e.item)

    @ui.page('/')
    def page():
        factory = FlexTableFactory(on_item_click=on_click)
        factory.create_container()
        factory.update_items(disabled_items)
        refs.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')

    factory = refs[0]
    factory.handle_item_click(0)
    factory.handle_item_click(1)
    screen.wait(0.1)

    assert len(clicked_items) == 2
    assert clicked_items[0] == disabled_items[0]
    assert clicked_items[1] == disabled_items[1]
