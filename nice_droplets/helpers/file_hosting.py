import os
from typing import Callable, Dict, Optional
from nicegui import ui
from fastapi import Request, HTTPException, Response

class FileHostingPage:
    """
    Helper class to register a file hosting page and allow plugin registration for sub-paths.
    Plugins are callables that accept (sub_path: str, request: Request) and return a Response or raise HTTPException.
    """
    def __init__(self, base_path: str = '/files'):
        self.base_path = base_path.rstrip('/')
        self.plugins: Dict[str, Callable[[str, Request], Response]] = {}
        self._register_page()

    def register_plugin(self, sub_path: str, handler: Callable[[str, Request], Response]):
        """
        Register a plugin handler for a given sub_path prefix (e.g., 'profile').
        """
        self.plugins[sub_path.strip('/')] = handler

    def _register_page(self):
        @ui.page(f'{self.base_path}/{{sub_path:path}}')
        async def file_hosting_endpoint(request: Request, sub_path: str):
            # sub_path: e.g. 'profile/123.jpg'
            parts = sub_path.split('/', 1)
            if not parts or parts[0] not in self.plugins:
                raise HTTPException(status_code=404, detail='Handler not found')
            plugin = self.plugins[parts[0]]
            plugin_subpath = parts[1] if len(parts) > 1 else ''
            return await plugin(plugin_subpath, request)
