import pytest
from typing import Any, Callable
from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.factories.flex_list_factory import FlexListFactory
from nice_droplets.events import FlexFactoryItemClickedArguments
from nice_droplets.elements.flex_list import FlexList
from nice_droplets.elements.search_list import SearchList
from nice_droplets.elements.typeahead import Typeahead

def test_create_by_name(screen: Screen):
    """Test that create_by_name works even without explicitly importing factory classes.
    
    This test only imports FlexListFactory, but create_by_name should still be able
    to find and instantiate all factory types because it imports the factories module
    which loads all subclasses.
    """
    screen.open('/')
    
    # Test exact matches - note we don't need to import the actual classes
    list_factory = FlexListFactory.create_by_name("List")
    assert list_factory.__class__.__name__ == "FlexListFactory"
    
    item_list_factory = FlexListFactory.create_by_name("Item")  # Changed from "ItemList" to "Item"
    assert item_list_factory.__class__.__name__ == "FlexItemListFactory"
    
    table_factory = FlexListFactory.create_by_name("Table")
    assert table_factory.__class__.__name__ == "FlexTableFactory"
    
    default_factory = FlexListFactory.create_by_name("Default")
    assert default_factory.__class__.__name__ == "FlexDefaultFactory"
    
    # Test case-insensitive matches
    assert FlexListFactory.create_by_name("list").__class__.__name__ == "FlexListFactory"
    assert FlexListFactory.create_by_name("ITEM").__class__.__name__ == "FlexItemListFactory"
    assert FlexListFactory.create_by_name("table").__class__.__name__ == "FlexTableFactory"
    assert FlexListFactory.create_by_name("DEFAULT").__class__.__name__ == "FlexDefaultFactory"
    
    # Test capital letters matches (based on short_name capitals)
    assert FlexListFactory.create_by_name("I").__class__.__name__ == "FlexItemListFactory"  # From "Item"
    assert FlexListFactory.create_by_name("i").__class__.__name__ == "FlexItemListFactory"  # Case-insensitive
    
    # Test invalid name
    with pytest.raises(ValueError) as exc_info:
        FlexListFactory.create_by_name("NonExistent")
    assert "No factory found with name 'NonExistent'" in str(exc_info.value)
    assert "Available factories: " in str(exc_info.value)

def test_component_string_factory(screen: Screen):
    """Test that components accept string factory names."""
    # Create UI elements before opening screen
    # Test FlexList with string factory
    flex_list = FlexList(factory="Item")
    assert flex_list._view_factory.__class__.__name__ == "FlexItemListFactory"
    
    # Test SearchList with string factory
    search_list = SearchList(factory="Table")
    assert search_list._view_factory.__class__.__name__ == "FlexTableFactory"
    
    # Test Typeahead with string factory
    typeahead = Typeahead(factory="Default")
    assert typeahead._search_list._view_factory.__class__.__name__ == "FlexDefaultFactory"
    
    # Test with capital letter versions
    flex_list = FlexList(factory="I")  # "I" for "Item"
    assert flex_list._view_factory.__class__.__name__ == "FlexItemListFactory"
    
    search_list = SearchList(factory="T")  # "T" for "Table"
    assert search_list._view_factory.__class__.__name__ == "FlexTableFactory"
    
    typeahead = Typeahead(factory="D")  # "D" for "Default"
    assert typeahead._search_list._view_factory.__class__.__name__ == "FlexDefaultFactory"
    
    # Open screen after creating elements
    screen.open('/')
