import pytest
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_item_list_factory import FlexItemListFactory
from nice_droplets import dui
from nice_droplets.elements.item_section import ItemSection


def test_item_list_factory_initialization(screen: Screen):
    """Test factory initialization with different configurations."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory1 = FlexItemListFactory()
        factory2 = FlexItemListFactory(bordered=True, separator=True, padding=True)
        factory_ref.append((factory1, factory2))

    screen.open('/')
    screen.wait(0.3)

    factory1, factory2 = factory_ref[0]
    assert factory1._list_kwargs == {}
    assert factory2._list_kwargs == {'bordered': True, 'separator': True, 'padding': True}


def test_item_list_factory_container_creation(screen: Screen):
    """Test container creation with different configurations."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory = FlexItemListFactory(bordered=True, separator=True)
        container = factory.create_container()
        factory_ref.append((factory, container))

    screen.open('/')
    screen.wait(0.3)

    factory, container = factory_ref[0]
    assert isinstance(container, dui.list)
    assert container._props.get('bordered') is True
    assert container._props.get('separator') is True


def test_item_list_factory_with_string_items(screen: Screen):
    """Test creating items from strings."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
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
    assert all(isinstance(elem, dui.item) for elem in factory._item_elements)
    assert all(elem._props.get('clickable') for elem in factory._item_elements)


def test_item_list_factory_with_dict_items(screen: Screen):
    """Test creating items from dictionaries with various properties."""
    factory_ref = []
    dict_items = [
        {'title': 'Item 1', 'subtitle': 'Description 1', 'avatar': 'mdi-account'},
        {'title': 'Item 2', 'subtitle': 'Description 2', 'avatar': 'https://example.com/avatar.jpg', 'avatar_round': True},
        {'title': 'Item 3', 'disabled': True}
    ]

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
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
    assert factory._item_elements[2]._props.get('clickable') is False


def test_item_list_factory_selection(screen: Screen):
    """Test item selection handling."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory._item_elements[1]._props['active'] = True
    screen.wait(0.1)
    assert factory._item_elements[1]._props.get('active') is True

    factory._item_elements[1]._props['active'] = None
    screen.wait(0.1)
    assert factory._item_elements[1]._props.get('active') is None


def test_item_list_factory_click_handling(screen: Screen):
    """Test item click event handling."""
    factory_ref = []
    clicked_item = None
    string_items = ['Item 1', 'Item 2', 'Item 3']

    def on_click(e):
        nonlocal clicked_item
        clicked_item = e.item

    @ui.page('/')
    def page():
        factory = FlexItemListFactory(on_item_click=on_click)
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.handle_item_click(0)
    screen.wait(0.1)
    assert clicked_item == string_items[0]


def test_item_list_factory_avatar_handling(screen: Screen):
    """Test avatar creation with different types."""
    factory_ref = []
    items = [
        {'title': 'Icon Avatar', 'avatar': 'mdi-account'},
        {'title': 'Image Avatar', 'avatar': 'https://example.com/avatar.jpg', 'avatar_round': True}
    ]

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Icon Avatar')
    screen.should_contain('Image Avatar')

    factory = factory_ref[0]
    first_item = factory._item_elements[0]
    sections = [child for child in first_item.default_slot if isinstance(child, dui.item_section)]
    assert any(section._props.get('avatar') for section in sections)


def test_item_list_factory_disable_enable(screen: Screen):
    """Test item disable/enable functionality."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
        factory.create_container()
        factory.update_items(string_items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.disable_item(0)
    screen.wait(0.1)
    assert 'disabled' in factory._item_elements[0]._classes

    factory.enable_item(0)
    screen.wait(0.1)
    assert 'disabled' not in factory._item_elements[0]._classes


def test_item_list_factory_with_empty_items(screen: Screen):
    """Test handling empty items list."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
        factory.create_container()
        factory.update_items([])
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0


def test_item_list_factory_clear(screen: Screen):
    """Test clearing items."""
    factory_ref = []
    string_items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
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


def test_item_list_factory_subtitle_handling(screen: Screen):
    """Test subtitle/caption handling."""
    factory_ref = []
    items = [
        {'title': 'Item 1', 'subtitle': 'Description 1'},
        {'title': 'Item 2', 'caption': 'Caption 2'}
    ]

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    screen.should_contain('Item 1')
    screen.should_contain('Description 1')
    screen.should_contain('Item 2')
    screen.should_contain('Caption 2')


def test_item_list_factory_non_string_items(screen: Screen):
    """Test handling non-string/non-dict items."""
    factory_ref = []
    items = [123, 456, 789]

    @ui.page('/')
    def page():
        factory = FlexItemListFactory()
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
