from nicegui import ui
from .settings_page_base import SettingsPage
from nice_droplets.helpers.config_interface import ConfigInterface

class SettingsPanel:
    """A panel with vertical tabs to switch between multiple SettingsPages."""
    def __init__(self, pages: list[SettingsPage], width: int = 800, height: int = 600):
        self.pages = pages
        self.width = width
        self.height = height
        self.settings_tab = None

    async def build(self):
        with ui.element('div').classes(
            'flex justify-center items-center w-full h-full'
        ):
            with ui.card().classes(
                'flex flex-row shadow-lg rounded-lg glass-container no-zoom'
            ).style(f'width: {self.width}px; height: {self.height}px;'):
                with ui.element('div').classes('flex flex-row w-full h-full'):
                    # Tab selection state
                    if self.settings_tab is None:
                        self.settings_tab = self.pages[0].short_name
                    with ui.element('div').classes('flex flex-col w-48 border-r'):
                        with ui.tabs().props('vertical').classes('flex flex-col w-full').bind_value(self, 'settings_tab'):
                            for page in self.pages:
                                ui.tab(page.short_name, icon=page.icon).props('vertical')
                    with ui.tab_panels().classes('flex-1 w-0 overflow-auto glass-container no-zoom min-w-0 max-w-full overflow-x-hidden') \
                        .props('vertical').bind_value(self, 'settings_tab'):
                        for idx, page in enumerate(self.pages):
                            with ui.tab_panel(page.short_name):
                                await page.build()
