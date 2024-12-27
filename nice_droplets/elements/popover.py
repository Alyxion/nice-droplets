import uuid

from nicegui import ui
from nicegui.element import Element
from nicegui.events import Handler, handle_event, GenericEventArguments

from nice_droplets.events import ShowPopoverEventArguments, HidePopoverEventArguments


class Popover(Element, component='popover.js'):
    def __init__(self,
                 *,
                 on_show: Handler[ShowPopoverEventArguments] | None = None,
                 on_hide: Handler[HidePopoverEventArguments] | None = None,
                 observe_parent: bool = True,
                 show_events: list[str] | None = None,
                 hide_events: list[str] | None = None,
                 ):
        super().__init__()
        self._props['showEvents'] = show_events or ['focus']
        self._props['hideEvents'] = hide_events or ['blur']
        self._show_handlers = [on_show] if on_show else []
        self._hide_handlers = [on_hide] if on_hide else []
        self._targets: dict[int, Element] = {}
        if observe_parent and self.parent_slot:
            self.add_target(self.parent_slot.parent)
        self.on('_show', self._handle_show)
        self.on('_hide', self._handle_hide)

    def on_show(self, handler: Handler[ShowPopoverEventArguments]):
        """Add a callback to be invoked when the popover is shown."""
        self._show_handlers.append(handler)

    def on_hide(self, handler: Handler[HidePopoverEventArguments]):
        """Add a callback to be invoked when the popover is hidden."""
        self._hide_handlers.append(handler)

    def show_at(self, target: Element):
        """Show the popover at the given target."""
        self.run_method('show_at', target.id)

    def hide(self):
        """Hide the popover."""
        self.run_method('hide')

    def add_target(self, element: Element):
        self.run_method('attachElement', element.id)
        self._targets[element.id] = element

    def remove_target(self, element: Element):
        if element.id not in self._targets:
            return
        del self._targets[element.id]
        self.run_method('detachElement', element.id)

    def _handle_show(self, element_id: int) -> None:
        target = self._targets.get(element_id, None)
        if target is None:
            return
        arguments = ShowPopoverEventArguments(sender=self)
        for handler in self._show_handlers:
            handle_event(handler, arguments)
