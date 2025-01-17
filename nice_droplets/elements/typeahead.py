from typing import Any, Callable, Union
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
                 factory: Union[FlexListFactory, str] | None = None,
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
        :param factory: Factory to use for creating the flex views. Can be either a FlexListFactory instance
                      or a string name (e.g., "Item", "Table", "Default", or their capital letter versions like "I", "T", "D")
        :param on_show: Handler for when the popover is shown.
        :param on_hide: Handler for when the popover is hidden.
        :param on_value_select: Optional callback for handling value selection for this element
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
        self._element_value_selects: dict[Element, Handler[TypeaheadValueSelectEventArguments]] = {}
        self._element_searches: dict[Element, Callable[[str], QueryTask]] = {}
        
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
                min_chars=min_chars,
                debounce=debounce,
                on_click=lambda item: self._handle_item_select(item),
                on_content_update=self._handle_content_update,
                on_search=on_search,
                factory=factory
            )

        if observe_parent:
            parent = ui.context.slot.parent            
            self.observe(parent, on_value_select=on_value_select, on_search=on_search)

    def observe(self, element: Element, *, 
               on_value_select: Handler[TypeaheadValueSelectEventArguments] | None = None,
               on_search: Callable[[str], QueryTask] | None = None):
        """Observe an element for focus events to show typeahead suggestions.
        
        :param element: The element to observe
        :param on_value_select: Optional callback for handling value selection for this element
        :param on_search: Optional callback for handling search for this element
        """
        super().observe(element)
        if isinstance(element, ValueElement):
            element.on('keydown', self._handle_key)
            element.on_value_change(self._handle_input_change)
            if not on_value_select:
                on_value_select = lambda e: str(e.item)
            self._element_value_selects[element] = on_value_select
            if on_search:
                self._element_searches[element] = on_search

    def unobserve(self, element: Element):
        """Stop observing an element for focus events."""
        super().unobserve(element)
        if self._current_target and self._current_target == element:
            self._remove_current_target()
        if element in self._element_value_selects:
            del self._element_value_selects[element]
        if element in self._element_searches:
            del self._element_searches[element]

    async def _handle_key(self, e: GenericEventArguments) -> None:
        """Handle keyboard events."""
        if self._hot_key_handler.verify('showSuggestions', e):
            self.show_at(e.sender)
            return

        if e.sender != self._current_target:
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
        
        # Set the search handler for the current target
        if self._current_target in self._element_searches:
            self._search_list.set_search_handler(self._element_searches[self._current_target])
        
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
        
        # Create event arguments
        event_args = TypeaheadValueSelectEventArguments(client=self.client, sender=self, item=e.item)
        
        # Try element-specific handler first, then fall back to global handler
        for element, handler in self._element_value_selects.items():
            value = handler(event_args)
            if value is not None:
                element.set_value(value)
        
        self._search_list.set_search_query('')
        self.hide()

    def _handle_content_update(self, e: SearchListContentUpdateEventArguments) -> None:
        """Handle when the search list content is updated."""
        self.keep_hidden = len(self._search_list.items) == 0 or not self._current_target
