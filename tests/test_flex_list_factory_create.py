import pytest
from typing import Any, Callable
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_list_factory import FlexListFactory
from nice_droplets.events import FlexFactoryItemClickedArguments
from nice_droplets import dui


def test_create_by_name(screen: Screen):
    """Test that create_by_name works even without explicitly importing factory classes."""
    results = []

    @ui.page('/')
    def page():
        # Test exact matches
        list_factory = FlexListFactory.create_by_name("List")
        item_list_factory = FlexListFactory.create_by_name("Item")
        table_factory = FlexListFactory.create_by_name("Table")
        default_factory = FlexListFactory.create_by_name("Default")

        results.append({
            'list': list_factory.__class__.__name__,
            'item': item_list_factory.__class__.__name__,
            'table': table_factory.__class__.__name__,
            'default': default_factory.__class__.__name__,
            'list_lower': FlexListFactory.create_by_name("list").__class__.__name__,
            'item_upper': FlexListFactory.create_by_name("ITEM").__class__.__name__,
            'table_lower': FlexListFactory.create_by_name("table").__class__.__name__,
            'default_upper': FlexListFactory.create_by_name("DEFAULT").__class__.__name__,
            'i_short': FlexListFactory.create_by_name("I").__class__.__name__,
            'i_lower': FlexListFactory.create_by_name("i").__class__.__name__,
        })

    screen.open('/')
    screen.wait(0.3)

    r = results[0]
    assert r['list'] == "FlexListFactory"
    assert r['item'] == "FlexItemListFactory"
    assert r['table'] == "FlexTableFactory"
    assert r['default'] == "FlexDefaultFactory"
    assert r['list_lower'] == "FlexListFactory"
    assert r['item_upper'] == "FlexItemListFactory"
    assert r['table_lower'] == "FlexTableFactory"
    assert r['default_upper'] == "FlexDefaultFactory"
    assert r['i_short'] == "FlexItemListFactory"
    assert r['i_lower'] == "FlexItemListFactory"

    # Test invalid name
    with pytest.raises(ValueError) as exc_info:
        FlexListFactory.create_by_name("NonExistent")
    assert "No factory found with name 'NonExistent'" in str(exc_info.value)
    assert "Available factories: " in str(exc_info.value)


def test_component_string_factory(screen: Screen):
    """Test that components accept string factory names."""
    refs = []

    @ui.page('/')
    def page():
        flex_list = dui.flex_list(factory="Item")
        search_list = dui.search_list(factory="Table")
        typeahead = dui.typeahead(factory="Default")

        flex_list2 = dui.flex_list(factory="I")
        search_list2 = dui.search_list(factory="T")
        typeahead2 = dui.typeahead(factory="D")

        refs.append({
            'flex_list': flex_list._view_factory.__class__.__name__,
            'search_list': search_list._view_factory.__class__.__name__,
            'typeahead': typeahead._search_list._view_factory.__class__.__name__,
            'flex_list2': flex_list2._view_factory.__class__.__name__,
            'search_list2': search_list2._view_factory.__class__.__name__,
            'typeahead2': typeahead2._search_list._view_factory.__class__.__name__,
        })

    screen.open('/')
    screen.wait(0.3)

    r = refs[0]
    assert r['flex_list'] == "FlexItemListFactory"
    assert r['search_list'] == "FlexTableFactory"
    assert r['typeahead'] == "FlexDefaultFactory"
    assert r['flex_list2'] == "FlexItemListFactory"
    assert r['search_list2'] == "FlexTableFactory"
    assert r['typeahead2'] == "FlexDefaultFactory"
