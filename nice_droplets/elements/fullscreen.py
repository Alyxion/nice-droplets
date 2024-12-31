from nicegui import ui

class Fullscreen:
    """Manages fullscreen mode for the application"""

    def __init__(self):
        pass

    async def get_state(self) -> bool:
        """Get current fullscreen state"""
        return await ui.run_javascript('return document.fullscreenElement !== null;')

    def enter(self, block_escape_key: bool = False) -> None:
        """Enter fullscreen mode.

        :param block_escape_key: Prevent escape key from exiting fullscreen. Note that only some browsers support this such as Google Chrome or Microsoft Edge.
        """
        script = 'document.documentElement.requestFullscreen()'
        if block_escape_key:
            script += '; navigator.keyboard.lock(["Escape"]);'
        ui.run_javascript(script)        

    def exit(self) -> None:
        """Exit fullscreen mode"""
        ui.run_javascript('document.exitFullscreen();')

    async def toggle(self, block_escape_key: bool = False) -> None:
        """Toggle fullscreen mode"""
        if await self.get_state():
            await self.exit()
        else:
            await self.enter(block_escape_key=block_escape_key)
