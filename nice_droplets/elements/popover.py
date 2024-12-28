import uuid

from nicegui import ui
from nicegui.element import Element
from nicegui.events import Handler, handle_event, GenericEventArguments

from nice_droplets.events import ShowPopoverEventArguments, HidePopoverEventArguments


class Popover(Element, component='popover.js'):
    VALID_VERTICALS = ['top', 'bottom']
    VALID_HORIZONTALS = ['left', 'right']

    POPOVER_DEFAULT_STYLE = 'padding: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'

    def __init__(self,
                 *,
                 on_show: Handler[ShowPopoverEventArguments] | None = None,
                 on_hide: Handler[HidePopoverEventArguments] | None = None,
                 observe_parent: bool = True,
                 default_style: bool = True,
                 show_events: list[str] | None = None,
                 hide_events: list[str] | None = None,
                 docking_side: str = 'bottom left',
                 ):
        # get current context element
        with ui.teleport('body'):
            super().__init__()
        if default_style:
            self.classes('bg-white dark:!bg-gray-800').style(self.POPOVER_DEFAULT_STYLE)
        self._props['showEvents'] = show_events or ['focus']
        self._props['hideEvents'] = hide_events or ['blur']
        components = docking_side.split(' ')
        valid_verticals = ['top', 'bottom']
        valid_horizontals = ['left', 'right']
        horizontals_found = [c for c in components if c in valid_horizontals]
        verticals_found = [c for c in components if c in valid_verticals]
        if len(verticals_found) == 0 and len(horizontals_found) == 0:
            raise ValueError(
                f"You need to specify at least a vertical or a horizontal component in the docking side. Got: {docking_side}")
        if len(verticals_found) > 1 or len(horizontals_found) > 1:
            raise ValueError(
                f"You can only specify one vertical and one horizontal component in the docking side. Got: {docking_side}")
        self._props['dockingSide'] = docking_side  # Store the property
        self._show_handlers = [on_show] if on_show else []
        self._hide_handlers = [on_hide] if on_hide else []
        self._targets: dict[int, Element] = {}
        if observe_parent:
            self.add_target(ui.context.slot.parent)
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

    def _handle_show(self, e: GenericEventArguments) -> None:
        target = self._targets.get(e.args['target'], None)
        if target is None:
            return
        arguments = ShowPopoverEventArguments(sender=self, client=self.client, target=target)
        for handler in self._show_handlers:
            handle_event(handler, arguments)

    def _handle_hide(self, e: GenericEventArguments) -> None:
        arguments = HidePopoverEventArguments(sender=self, client=self.client)
        for handler in self._hide_handlers:
            handle_event(handler, arguments)
