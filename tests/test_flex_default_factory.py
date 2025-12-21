import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_default_factory import FlexDefaultFactory


def test_default_factory_container_creation(screen: Screen):
    """Test container creation and styling."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        container = factory.create_container()
        factory_ref.append((factory, container))

    screen.open('/')
    screen.wait(0.3)

    factory, container = factory_ref[0]
    assert isinstance(container, ui.element)
    assert 'flex' in container._classes
    assert 'flex-col' in container._classes
    assert 'gap-1' in container._classes
    assert 'min-w-[200px]' in container._classes


def test_default_factory_with_string_items(screen: Screen):
    """Test creating items from strings."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = factory_ref[0]
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3

    # Check item styling
    first_item = factory._item_elements[0]
    assert 'cursor-pointer' in first_item._classes
    assert 'hover:bg-gray-100' in first_item._classes


def test_default_factory_with_dict_items(screen: Screen):
    """Test creating items from dictionaries."""
    factory_ref = []
    dict_items = [
        {'label': 'Item 1'},
        {'label': 'Item 2'},
        {'label': 'Item 3', 'disabled': True}
    ]

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(dict_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = factory_ref[0]
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3


def test_default_factory_selection(screen: Screen):
    """Test item selection styling."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]

    # Test selection
    factory._item_elements[1].classes('bg-primary text-white', remove='hover:bg-gray-100')
    screen.wait(0.1)
    assert 'bg-primary' in factory._item_elements[1]._classes
    assert 'text-white' in factory._item_elements[1]._classes
    assert 'hover:bg-gray-100' not in factory._item_elements[1]._classes

    # Test deselection
    factory._item_elements[1].classes('hover:bg-gray-100', remove='bg-primary text-white')
    screen.wait(0.1)
    assert 'bg-primary' not in factory._item_elements[1]._classes
    assert 'text-white' not in factory._item_elements[1]._classes
    assert 'hover:bg-gray-100' in factory._item_elements[1]._classes


def test_default_factory_click_handling(screen: Screen):
    """Test item click event handling."""
    factory_ref = []
    clicked_item = None
    string_items = ['Item 1', 'Item 2', 'Item 3']

    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.on_click(on_click)
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.handle_item_click(0)
    screen.wait(0.1)
    assert clicked_item == string_items[0]


def test_default_factory_with_empty_items(screen: Screen):
    """Test handling empty items list."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items([])
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0


def test_default_factory_clear(screen: Screen):
    """Test clearing items."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Item 2')
    screen.should_contain('Item 3')

    factory = factory_ref[0]
    assert len(factory._items) == 3

    factory.clear()
    screen.wait(0.1)
    screen.should_not_contain('Item 1')
    screen.should_not_contain('Item 2')
    screen.should_not_contain('Item 3')
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0


def test_default_factory_with_non_string_items(screen: Screen):
    """Test handling non-string/non-dict items."""
    factory_ref = []
    items = [123, 456, 789]

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('123')
    screen.should_contain('456')
    screen.should_contain('789')

    factory = factory_ref[0]
    assert len(factory._items) == 3


def test_default_factory_dict_without_label(screen: Screen):
    """Test handling dictionary items without label field."""
    factory_ref = []
    items = [{'other_field': 'value'}]

    @ui.page('/')
    def page():
        factory = FlexDefaultFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert len(factory._items) == 1
