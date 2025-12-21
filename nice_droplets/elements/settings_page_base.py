from nicegui import ui
from nice_droplets.helpers.config_interface import ConfigInterface

class SettingsPage:
    """Base class for a settings page with helpers for stream-forward UI creation and config binding."""
    def __init__(self, short_name: str, long_name: str, icon: str = None, config: ConfigInterface = None):
        self.short_name = short_name
        self.long_name = long_name
        self.icon = icon
        self.config = config

    async def build(self):
        with ui.row().classes("items-center gap-2 mb-4"):
            if self.icon:
                ui.icon(self.icon)
            ui.label(self.long_name).classes("text-xl font-bold")
        await self.build_content()

    async def build_content(self):
        """Override to build the page content (after the header)."""
        raise NotImplementedError("SettingsPage.build_content() must be implemented by subclasses.")

    async def add_checkbox(self, label: str = None, config_key: str = None, default: bool = False, row_label: str = None, **kwargs):
        """
        Add a checkbox in its own row. If config_key is provided, binds value to config.
        Optionally provide a row_label that appears left of the control.
        Returns the ui.checkbox instance.
        """
        initial = default
        if config_key and self.config:
            val = await self.config.async_get(config_key, default)
            initial = bool(val)
        with ui.row().classes('items-center gap-4'):
            checkbox = ui.checkbox(label, value=initial, **kwargs)
            if row_label:
                ui.label(row_label).classes('min-w-[140px]')
            if config_key and self.config:
                async def on_change(e):
                    await self.config.async_set(config_key, e.value)
                checkbox.on_value_change(on_change)
        return checkbox

    async def add_switch(self, label: str = None, config_key: str = None, default: bool = False, row_label: str = None, **kwargs):
        """
        Add a switch in its own row. If config_key is provided, binds value to config.
        Optionally provide a row_label that appears left of the control.
        Returns the ui.switch instance.
        """
        initial = default
        if config_key and self.config:
            val = await self.config.async_get(config_key, default)
            initial = bool(val)
        with ui.row().classes('items-center gap-4'):
            switch = ui.switch(label, value=initial, **kwargs)
            if row_label:
                ui.label(row_label).classes('min-w-[140px]')
            if config_key and self.config:
                async def on_change(e):
                    await self.config.async_set(config_key, e.value)
                switch.on_value_change(on_change)
        return switch

    async def add_select(self, label: str = None, options=None, config_key: str = None, default=None, row_label: str = None, **kwargs):
        """
        Add a select dropdown in its own row. If config_key is provided, binds value to config.
        Optionally provide a row_label that appears left of the control.
        Returns the ui.select instance.
        """
        initial = default
        if config_key and self.config:
            val = await self.config.async_get(config_key, default)
            initial = val
            # use default if val is invalid
            if val not in options:
                initial = default
        with ui.row().classes('items-center gap-4'):
            if row_label:
                ui.label(row_label).classes('min-w-[140px]')
            select = ui.select(options=options, value=initial, label=label, **kwargs)
            if config_key and self.config:
                async def on_change(e):
                    await self.config.async_set(config_key, e.value)
                select.on_value_change(on_change)
        return select

    async def add_custom(self, factory, config_key: str = None, default=None, row_label: str = None, on_change=None, **kwargs):
        """
        Add a custom component in its own row. Optionally bind value to config_key.
        The factory should accept (value, **kwargs) and return a component with .on('update:model-value', handler).
        Optionally provide a row_label that appears left of the control.
        Returns the created component.
        """
        initial = default
        if config_key and self.config:
            val = await self.config.async_get(config_key, default)
            initial = val
        with ui.row().classes('items-center gap-4'):
            if row_label:
                ui.label(row_label).classes('min-w-[140px]')
            component = factory(initial, **kwargs)
            if config_key and self.config:
                async def _on_change(e):
                    await self.config.async_set(config_key, e.value)
                    if on_change:
                        await on_change(e)
                component.on_value_change(_on_change)
            elif on_change:
                component.on_value_change(on_change)
        return component
