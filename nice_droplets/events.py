from dataclasses import dataclass

from nicegui.dataclasses import KWONLY_SLOTS
from nicegui.element import Element
from nicegui.events import UiEventArguments


@dataclass(**KWONLY_SLOTS)
class ShowPopoverEventArguments(UiEventArguments):
    target: Element


@dataclass(**KWONLY_SLOTS)
class HidePopoverEventArguments(UiEventArguments):
    pass
