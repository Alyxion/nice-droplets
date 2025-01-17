from typing import Any
from dataclasses import dataclass

from nicegui.dataclasses import KWONLY_SLOTS
from nicegui.element import Element
from nicegui.events import UiEventArguments, EventArguments


@dataclass(**KWONLY_SLOTS)
class TypeaheadValueSelectEventArguments(UiEventArguments):
    """Arguments for when a value is selected in a typeahead."""
    item: Any


@dataclass(**KWONLY_SLOTS)
class ShowPopoverEventArguments(UiEventArguments):
    target: Element


@dataclass(**KWONLY_SLOTS)
class HidePopoverEventArguments(UiEventArguments):
    pass


@dataclass(**KWONLY_SLOTS)
class SearchListContentUpdateEventArguments(UiEventArguments):
    """Event arguments for when a search list's content is updated."""
    items: list[Any]


@dataclass(**KWONLY_SLOTS)
class FlexFactoryItemClickedArguments(EventArguments):    
    sender: Any
    item: Any
    index: int
    element: Element | None = None



@dataclass(**KWONLY_SLOTS)
class FlexListItemClickedArguments(UiEventArguments):    
    item: Any
    index: int
    element: Element | None = None
