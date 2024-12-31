from typing import Any, Dict, Union
from nicegui.events import GenericEventArguments

HotKeyDefinition = Union[str, Dict[str, Any]]

class HotKeyHandler:
    """Handles keyboard shortcuts and hotkey verification"""

    def __init__(self, hot_keys: Dict[str, HotKeyDefinition] | None = None):
        """Initialize the hotkey handler.
        
        :param hot_keys: Dictionary mapping hotkey names to their definitions.
                      A definition can be either a simple key string or a dict
                      of event properties to match (e.g. {'key': 'a', 'ctrlKey': True}).
        """
        self.hot_keys = hot_keys or {}

    def verify(self, hotkey_name: str, e: GenericEventArguments) -> bool:
        """Check if an event matches a hotkey definition.
        
        :param hotkey_name: Name of the hotkey to check
        :param e: Keyboard event to verify
        :return: True if the event matches the hotkey definition
        """
        if hotkey_name not in self.hot_keys:
            return False
            
        hotkey = self.hot_keys[hotkey_name]
        if isinstance(hotkey, dict):
            return all(e.args.get(k) == v for k, v in hotkey.items())
        else:
            return e.args.get('key') == hotkey
