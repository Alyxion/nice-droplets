from typing import Any, Callable
from nicegui import ui
from nicegui.element import Element
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.events import ValueChangeEventArguments, GenericEventArguments, Handler

from nice_droplets.elements.popover import Popover
from nice_droplets.elements.search_list import SearchList
from nice_droplets.components import EventHandlerTracker
from nice_droplets.tasks.query_task import QueryTask
from nice_droplets.components.hot_key_handler import HotKeyHandler
from nice_droplets.events import (
    SearchListContentUpdateEventArguments,
    ShowPopoverEventArguments,
    HidePopoverEventArguments,
    TypeaheadValueSelectEventArguments
)
from nice_droplets.factories import FlexListFactory


class Typeahead(Popover):
    """A typeahead component that shows suggestions below and input field or table cell as you type.
    
    This component extends the Popover component to provide typeahead functionality
    for any ValueElement (like input, select, etc.).
    """

    def __init__(self,
                 *,
                 on_search: Callable[[str], QueryTask] | None = None,
                 min_chars: int = 1,
                 debounce: float = 0.1,
                 on_click: Callable[[Any], None] | None = None,
                 observe_parent: bool = True,     
                 factory: FlexListFactory | None = None,
                 on_show: Handler[ShowPopoverEventArguments] | None = None,
                 on_hide: Handler[HidePopoverEventArguments] | None = None,
                 on_value_select: Handler[TypeaheadValueSelectEventArguments] | None = None,
                 **kwargs            
                 ):
        """Initialize the typeahead component.
        
        :param on_search: Function that creates a search task for a query.
        :param min_chars: Minimum number of characters required to start a search.
        :param debounce: Time to wait before executing a search after input changes.
        :param on_click: Function to call when an item is clicked.
        :param observe_parent: Whether to observe the parent element for focus events.
        :param factory: The factory to use for creating the flex list.
        :param on_show: Handler for when the popover is shown.
        :param on_hide: Handler for when the popover is hidden.
        :param value_callback: Function to convert a selected item to its string representation.
        :param kwargs: Additional arguments to pass to the Popover constructor.
        """
        # Set default popover properties while allowing overrides through kwargs
        popover_kwargs = {
            'show_events': ['focus', 'input'],
            'hide_events': ['blur'],
            'docking_side': 'bottom left',
            'observe_parent': False,
            'default_style': True,
            'on_show': on_show,
            'on_hide': on_hide,
            **kwargs
        }
        super().__init__(**popover_kwargs)
        self.keep_hidden = True
        self._current_target: ValueElement | None = None
        self._event_helper: EventHandlerTracker | None = None
        self._min_chars = min_chars
        self._selected_value = None
        self._on_value_select = on_value_select
        
        self._hot_key_handler = HotKeyHandler({
            'showSuggestions': {
                'key': ' ',
                'ctrlKey': True
            },
            'cancel': {
                'key': 'Escape'
            }
        })

        with self:
            self._search_list = SearchList(
                on_search=on_search,
                min_chars=min_chars,
                debounce=debounce,
                on_click=lambda item: self._handle_item_select(item),
                on_content_update=self._handle_content_update,
                factory=factory
            )

        if observe_parent:
            parent = ui.context.slot.parent
            self.observe(parent)

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

    async def _handle_key(self, e: GenericEventArguments) -> None:
        """Handle keyboard events."""
        if e.sender != self._current_target:
            return
            
        if self._hot_key_handler.verify('showSuggestions', e):
            self.show_at(e.sender)
            return

        if self._hot_key_handler.verify('cancel', e):
            self.hide()
            return

        if self._search_list._handle_key(e):
            pass

    def _handle_show(self, e: GenericEventArguments) -> None:
        super()._handle_show(e)
        new_target = self._targets.get(e.args['target'], None)
        if self._current_target == new_target:
            return
        self._remove_current_target()
        self._current_target = self._targets.get(e.args['target'], None)
        self._event_helper = EventHandlerTracker(self._current_target)
        self._search_list.set_search_query(self._current_target.value)

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
        if self._selected_value == e.value:  # catch once
            self._selected_value = None
            return
        self._search_list.set_search_query(e.value if e.value else '')

    def _handle_item_select(self, e: Any) -> None:
        """Handle when a suggestion item is selected."""
        if not self._current_target or not e.item:
            return
        
        # Create and emit event arguments
        event_args = TypeaheadValueSelectEventArguments(sender=self, item=e.item)
        if self._on_value_select:
            self._on_value_select(event_args)
        
        # Use event value or fallback to str
        value = event_args.value if event_args.value is not None else str(e.item)
        self._selected_value = value
        self._current_target.set_value(value)
        self._search_list.set_search_query('')
        self.hide()

    def _handle_content_update(self, e: SearchListContentUpdateEventArguments) -> None:
        """Handle when the search list content is updated."""
        self.keep_hidden = len(self._search_list.items) == 0 or not self._current_target
