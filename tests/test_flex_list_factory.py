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


def test_factory_initialization(screen: Screen):
    """Test factory initialization with and without click handler."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory1 = SampleFlexListFactory()
        def on_click(e): pass
        factory2 = SampleFlexListFactory(on_item_click=on_click)
        factory_ref.append((factory1, factory2))

    screen.open('/')
    screen.wait(0.3)

    factory1, factory2 = factory_ref[0]
    assert factory1.index == -1
    assert len(factory1._click_handler) == 0
    assert len(factory2._click_handler) == 1


def test_factory_index_management(screen: Screen):
    """Test index setting and management."""
    factory_ref = []

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.index = 1
    assert factory.index == 1
    assert factory._previous_index == -1

    factory.index = 2
    assert factory.index == 2
    assert factory._previous_index == 1


def test_factory_item_click_handling(screen: Screen):
    """Test item click event handling."""
    factory_ref = []
    clicked_data = None
    items = ['Item 1', 'Item 2', 'Item 3']

    def on_click(e: FlexFactoryItemClickedArguments):
        nonlocal clicked_data
        clicked_data = e.item

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory.on_click(on_click)
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.handle_item_click(0)
    assert clicked_data == 'Item 1'


def test_factory_item_state_management(screen: Screen):
    """Test item enable/disable functionality."""
    factory_ref = []
    items = [
        {'text': 'Item 1', 'disabled': True},
        {'text': 'Item 2', 'disabled': False},
        {'text': 'Item 3'}
    ]

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert factory.is_item_disabled(items[0]) is True
    assert factory.is_item_disabled(items[1]) is False
    assert factory.is_item_disabled(items[2]) is False


def test_factory_clear(screen: Screen):
    """Test clearing items."""
    factory_ref = []
    items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3

    factory.clear()
    assert len(factory._items) == 0
    assert len(factory._item_elements) == 0
    assert factory.index == -1
    assert factory._previous_index == -1


def test_factory_update_items(screen: Screen):
    """Test updating items."""
    factory_ref = []
    items = ['Item 1', 'Item 2', 'Item 3']

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    assert len(factory._items) == 3
    assert len(factory._item_elements) == 3

    new_items = ['New 1', 'New 2']
    factory.update_items(new_items)
    assert len(factory._items) == 2
    assert len(factory._item_elements) == 2
    assert factory._items == new_items


def test_factory_item_click_with_disabled(screen: Screen):
    """Test click handling with disabled items."""
    factory_ref = []
    clicked_items = []
    items = [
        {'text': 'Item 1', 'disabled': True},
        {'text': 'Item 2'}
    ]

    def on_click(e: FlexFactoryItemClickedArguments):
        clicked_items.append(e.item)

    @ui.page('/')
    def page():
        factory = SampleFlexListFactory()
        factory.on_click(on_click)
        factory.create_container()
        factory.update_items(items)
        factory_ref.append(factory)

    screen.open('/')
    screen.wait(0.3)

    factory = factory_ref[0]
    factory.handle_item_click(0)
    factory.handle_item_click(1)

    assert len(clicked_items) == 2
    assert clicked_items[0] == items[0]
    assert clicked_items[1] == items[1]
