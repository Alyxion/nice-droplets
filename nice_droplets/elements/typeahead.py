from typing import Any, Callable
from nicegui import ui
from nicegui.element import Element
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.events import ValueChangeEventArguments, GenericEventArguments

from nice_droplets.elements.popover import Popover
from nice_droplets.elements.search_list import SearchList
from nice_droplets.components import EventHandlerTracker

class Typeahead(Popover):
    """A typeahead component that shows suggestions as you type.
    
    This component extends the Popover component to provide typeahead functionality
    for any ValueElement (like input, select, etc.).
    """

    def __init__(self,
                 *,
                 on_search: Callable[[str], list[Any]] | None = None,
                 min_chars: int = 1,
                 debounce_ms: int = 300,
                 item_label: Callable[[Any], str] | None = None,
                 on_select: Callable[[Any], None] | None = None,
                 observe_parent: bool = True,
                 ):
        """Initialize the typeahead component.
        
        :param on_search: Callback function that takes a search string and returns a list of suggestions
        :param min_chars: Minimum number of characters before triggering search
        :param debounce_ms: Debounce time in milliseconds for search
        :param item_label: Function to convert an item to its display string (defaults to str)
        :param on_select: Callback function when an item is selected
        :param observe_parent: Whether to observe the parent element for changes
        """
        super().__init__(
            show_events=['focus', 'input'],
            hide_events=['blur'],
            docking_side='bottom left',
            observe_parent=False,
            default_style=True
        )
        self.keep_hidden = True
        self._current_target: ValueElement | None = None
        self._event_helper: EventHandlerTracker | None = None
        # TODO: Actually the keydown event should be attached upon show and detached upon hide
        # Due to a potential bug in Vue or NiceGUI this is not possible at the moment, see
        # https://github.com/zauberzeug/nicegui/issues/4154
        with self:
            self._search_list = SearchList(
                on_search=on_search,
                min_chars=min_chars,
                debounce_ms=debounce_ms,
                item_label=item_label,
                on_select=lambda item: self._handle_item_select(item)
            )
        if observe_parent:
            parent = ui.context.slot.parent
            self.observe(parent)

    def _handle_key(self, e: GenericEventArguments) -> None:
        """Handle keyboard events."""
        if e.sender != self._current_target:
            return
        if self._search_list.handle_key(e):
            pass
            # e.prevent_default = True

    def _handle_show(self, e: GenericEventArguments) -> None:
        super()._handle_show(e)
        new_target = self._targets.get(e.args['target'], None)
        if self._current_target == new_target:
            return
        self._remove_current_target()
        self._current_target = self._targets.get(e.args['target'], None)
        self._event_helper = EventHandlerTracker(self._current_target)

    def _remove_current_target(self) -> None:
        if self._current_target:
            self._current_target = None
            self._event_helper.remove()
            self._event_helper = None

    def _handle_hide(self, e: GenericEventArguments) -> None:
        self._remove_current_target()
        return super()._handle_hide(e)

    def _handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input value changes."""
        if e.sender != self._current_target:
            return
        self._search_list.handle_input_change(e)
        self.keep_hidden = len(str(e.value or '')) < self._search_list._min_chars

    def _handle_item_select(self, item: Any) -> None:
        """Handle when a suggestion item is selected."""
        # Update the value of the current target if it has a set_value method
        if not self._current_target:
            return
        self._current_target.set_value(item)
        self.hide()

    def observe(self, element: Element):
        """Observe an element for focus events to show typeahead suggestions."""
        super().observe(element)
        if isinstance(element, ValueElement):
            element.on('keydown', self._handle_key)
            element.on_value_change(self._handle_input_change)

    def unobserve(self, element: Element):
        """Stop observing an element for focus events."""
        super().unobserve(element)
        if self._current_target and self._current_target.id == element.id:
            self._remove_current_target()
