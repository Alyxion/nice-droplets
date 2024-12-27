import uuid

from nicegui import ui
from nicegui.element import Element


class Popover(Element, component='popover.js'):
    def __init__(self,
                 observe_parent: bool = True,
                 show_events: list[str] | None = None,
                 hide_events: list[str] | None = None,
                 ):
        super().__init__()
        self._props['showEvents'] = show_events or ['focus']
        self._props['hideEvents'] = hide_events or ['blur']
        if observe_parent and self.parent_slot:
            self.add_target(self.parent_slot.parent)

    def show_at(self, target: Element):
        """Show the popover at the given target."""
        self.run_method('show_at', target.id)

    def hide(self):
        """Hide the popover."""
        self.run_method('hide')

    def add_target(self, element: Element):
        self.run_method('attachElement', element.id)

    def remove_target(self, element: Element):
        self.run_method('detachElement', element.id)
