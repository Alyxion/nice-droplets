from typing import Any, Dict, List, TypeVar
from nicegui.element import Element, EventListener
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.events import ValueChangeEventArguments, Handler

T = TypeVar('T')

class EventHandlerTracker:
    """Helper class to track event handlers added to an element so they can be removed again
    which is currently not natively supported by NiceGUI."""

    def __init__(self, element: Element):
        self.element = element
        self._listener_ids: Dict[str, str] = {}
        self._old_listeners = None
        self._old_change_handlers: List[Handler[ValueChangeEventArguments]] | None = None

    def remove(self) -> None:
        if hasattr(self.element, '_event_listeners'):
            for listener_id in self._listener_ids.values():
                if listener_id in self.element._event_listeners:
                    del self.element._event_listeners[listener_id]
            self._listener_ids.clear()
        if isinstance(self.element, ValueElement):
            for handler in self._old_change_handlers or []:
                if handler in self.element._change_handlers:
                    self.element._change_handlers.remove(handler)
        self.element.update()

    def __enter__(self) -> Element:
        self._old_listeners = {
            listener_id: listener
            for listener_id, listener in self.element._event_listeners.items()
        }
        if isinstance(self.element, ValueElement):
            self._old_change_handlers = self.element._change_handlers.copy()
        return self.element

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            return
        current_listeners = self.element._event_listeners
        added_listener_ids = set(current_listeners.keys()) - set(self._old_listeners.keys())
        for listener_id in added_listener_ids:
            listener = current_listeners[listener_id]
            self._listener_ids[listener.type] = listener_id
        if isinstance(self.element, ValueElement):
            added_handlers = set(self.element._change_handlers) - set(self._old_change_handlers or [])
