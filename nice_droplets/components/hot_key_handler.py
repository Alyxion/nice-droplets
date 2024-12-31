from typing import Any, Dict, Union, List
from nicegui.events import GenericEventArguments

HotKeyDefinition = Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]

class HotKeyHandler:
    """Handles keyboard shortcuts and hotkey verification"""

    def __init__(self, hot_keys: Dict[str, HotKeyDefinition] | None = None):
        """Initialize the hotkey handler.
        
        :param hot_keys: Dictionary mapping hotkey names to their definitions.
                      A definition can be either:
                      - a simple key string
                      - a dict of event properties to match (e.g. {'key': 'a', 'ctrlKey': True})
                      - a list of either of the above
        """
        self.hot_keys = hot_keys or {}

    def verify(self, hotkey_name: str, e: GenericEventArguments) -> bool:
        """Check if an event matches a hotkey definition.
        
        :param hotkey_name: Name of the hotkey to check
        :param e: Keyboard event to verify
        :return: True if the event matches any of the hotkey definitions
        """
        if hotkey_name not in self.hot_keys:
            return False
            
        hotkey = self.hot_keys[hotkey_name]
        
        # Convert single definition to list for uniform handling
        if not isinstance(hotkey, list):
            hotkey = [hotkey]
            
        # Check if event matches any of the definitions
        for key_def in hotkey:
            if isinstance(key_def, dict):
                if all(e.args.get(k) == v for k, v in key_def.items()):
                    return True
            else:
                if e.args.get('key') == key_def:
                    return True
                
        return False
