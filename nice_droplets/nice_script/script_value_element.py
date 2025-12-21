from pydantic import BaseModel, Field
from nice_droplets.nice_script import ScriptElementConfig


class ScriptValueElementConfig(ScriptElementConfig):
    value: str | int | bool | float | None = Field(None, description="Value of the element")
    value_type: str = Field("str", description="Type of the value")

    def convert_value(self, value: str | int | bool | float | None) -> str | int | bool | float | None:
        if self.value_type == "str":
            return str(value)
        elif self.value_type == "int":
            return int(value)
        elif self.value_type == "bool":
            return bool(value)
        elif self.value_type == "float":
            return float(value)
        return value