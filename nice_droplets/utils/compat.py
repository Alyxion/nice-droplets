"""Compatibility utilities for supporting multiple NiceGUI versions."""

from nicegui import ui, __version__ as nicegui_version

# Parse major version
NICEGUI_MAJOR_VERSION = int(nicegui_version.split('.')[0])

# NiceGUI 3.x requires sanitize parameter for ui.html
NICEGUI_3_OR_LATER = NICEGUI_MAJOR_VERSION >= 3


def html(content: str, *, sanitize: bool = False, **kwargs) -> ui.html:
    """
    Create a ui.html element with version-compatible sanitize handling.
    
    In NiceGUI 3.x, the sanitize parameter is required.
    In NiceGUI 2.x, the sanitize parameter doesn't exist.
    
    Args:
        content: HTML content to display
        sanitize: Whether to sanitize the HTML (default: False for trusted content)
        **kwargs: Additional arguments passed to ui.html
    
    Returns:
        ui.html element
    """
    if NICEGUI_3_OR_LATER:
        return ui.html(content, sanitize=sanitize, **kwargs)
    else:
        return ui.html(content, **kwargs)
