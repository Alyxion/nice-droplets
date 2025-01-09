from typing import Optional, Self, TypedDict
from typing_extensions import NotRequired
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.events import Handler, handle_event, ClickEventArguments
from .item_section import ItemSection


class ItemKwargs(TypedDict):
    active: NotRequired[bool]
    clickable: NotRequired[bool]
    dense: NotRequired[bool]
    dark: NotRequired[bool]
    inset_level: NotRequired[int]
    tabindex: NotRequired[Optional[int | str]]
    manual_focus: NotRequired[bool]
    focused: NotRequired[bool]
    to: NotRequired[Optional[str | dict]]
    exact: NotRequired[bool]
    replace: NotRequired[bool]
    active_class: NotRequired[str]
    exact_active_class: NotRequired[str]


class Item(DisableableElement):
    # Map Python property names to Vue prop names
    _ITEM_PROPS = {
        'active': 'active',
        'clickable': 'clickable',
        'dense': 'dense',
        'dark': 'dark',
        'manual_focus': 'manual-focus',
        'focused': 'focused',
        'inset_level': 'inset-level',
        'tabindex': 'tabindex',
        'to': 'to',
        'exact': 'exact',
        'replace': 'replace',
        'active_class': 'active-class',
        'exact_active_class': 'exact-active-class'
    }

    def __init__(self, text: str = '', *, 
                 on_click: Optional[Handler[ClickEventArguments]] = None,
                 **kwargs: ItemKwargs) -> None:
        """List Item

        Creates a clickable list item based on Quasar's
        `QItem <https://quasar.dev/vue-components/list-and-list-items#qitem-api>`_ component.
        
        The item should be placed inside a ``ui.list`` or ``ui.menu`` element.
        If the text parameter is provided, an item section will be created with the given text.
        If you want to customize how the text is displayed, you need to create your own item section and label elements.

        :param text: text to be displayed
        :param on_click: callback to be executed when clicking on the item (sets the "clickable" prop to True)
        :param kwargs: Additional keyword arguments:
            - active (bool): is item active
            - clickable (bool): is item clickable
            - dense (bool): dense mode; occupies less space
            - dark (bool): applies a dark theme
            - inset_level (int): applies an inset to the content (0-16)
            - tabindex (Optional[int | str]): tabindex HTML attribute value
            - manual_focus (bool): enables manual focus management
            - focused (bool): is item focused
            - to (Optional[str | dict]): router link destination as string path or dict with path and parameters
            - exact (bool): match the exact route for active state
            - replace (bool): replace current route instead of pushing
            - active_class (str): class to apply when item is active
            - exact_active_class (str): class to apply when exact route is active
        """
        super().__init__(tag='q-item')

        # Set props if they exist in kwargs
        for py_prop, vue_prop in self._ITEM_PROPS.items():
            if py_prop in kwargs:
                self._props[vue_prop] = kwargs[py_prop]
            
        if on_click:
            self.on_click(on_click)

        if text:
            with self:
                ItemSection(text=text)

    def on_click(self, callback: Handler[ClickEventArguments]) -> Self:
        """Add a callback to be invoked when the List Item is clicked."""
        self._props['clickable'] = True  # idempotent
        self.on('click', lambda _: handle_event(callback, ClickEventArguments(sender=self, client=self.client)))
        return self
