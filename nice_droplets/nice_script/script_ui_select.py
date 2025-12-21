from nice_droplets.nice_script.script_value_element import ScriptValueElementConfig
from nicegui import ui
from pydantic import BaseModel, Field
from nice_droplets.nice_script.script_element import ScriptElementConfig


class ScriptUISelectConfig(ScriptValueElementConfig):
    options: dict[str, str] = Field(..., description="Options for the select")
    label: str | None = Field(None, description="Label for the select")

    async def build(self, *, values: dict[str, any]) -> ui.element | None:
        if self.name:
            value = None
            if self.name in values:
                value = values[self.name]
        select = ui.select(options=self.options, value=str(value), label=self.label)
        if self.name:
            async def on_change(e):
                values[self.name] = self.convert_value(e.value)
            select.on_value_change(on_change)
        return select