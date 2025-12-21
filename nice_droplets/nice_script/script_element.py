from nicegui import ui
from pydantic import BaseModel, Field


class ScriptElementConfig(BaseModel):
    name: str = Field("", description="Name of the script element")
    etype: str = Field("ui.element", description="Type of the script element")
    elements: list["ScriptElementConfig"] = Field(default_factory=list)
    description: str | None = Field(None, description="Description of the script element")
    
    async def build(self, *, values: dict[str, any]) -> ui.element | None:
        pass