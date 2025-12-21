from nicegui import ui
from pydantic import BaseModel, Field
from nice_droplets.nice_script import ScriptElementConfig, ScriptUISelectConfig

class NiceScriptSource(BaseModel):
    elements: list[ScriptElementConfig] = Field(default_factory=list)

class NiceScriptInstance:
    def __init__(self, *, values: dict[str, any], source: "NiceScript") -> None:
        self.values: dict[str, any] = values
        self.value_descriptions: dict[str, str] = {
            "user_time_zone": "Timezone of the user",
            "current_date_time": "Current date and time",
            "current_date": "Current date",
            "current_time_only": "Current time",
            "current_calendar_week": "Current calendar week",
            "current_weekday": "Current weekday",
            "current_month": "Current month",
            "current_year": "Current year",
            "current_day_of_year": "Current day of year",
            "current_day_of_month": "Current day of month",
            "current_day_of_week": "Current day of week"
        }
        self.source: "NiceScript" = source
        self.timezone: str = "UTC"

    def update_time_data(self, time_zone: str) -> None:
        """
        Updates time data in the values dictionary.

        :param time_zone: Timezone to use for time data
        """
        if not time_zone:
            time_zone = self.timezone
        else:
            self.timezone = time_zone
        import pytz
        import datetime
        tz = pytz.timezone(time_zone)
        self.values["user_time_zone"] = time_zone
        self.values["current_date_time"] = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        self.values["current_date"] = datetime.datetime.now(tz).strftime("%Y-%m-%d")
        self.values["current_time_only"] = datetime.datetime.now(tz).strftime("%H:%M:%S")        
        self.values["current_calendar_week"] = datetime.datetime.now(tz).isocalendar().week
        self.values["current_weekday"] = datetime.datetime.now(tz).strftime("%A")
        self.values["current_month"] = datetime.datetime.now(tz).strftime("%B")
        self.values["current_year"] = datetime.datetime.now(tz).strftime("%Y")
        self.values["current_day_of_year"] = datetime.datetime.now(tz).strftime("%j")
        self.values["current_day_of_month"] = datetime.datetime.now(tz).strftime("%d")
        self.values["current_day_of_week"] = datetime.datetime.now(tz).strftime("%w")

    async def build(self, *, build_ui: bool = True, default_values: bool = False, timezone: str | None = None) -> None:
        """
        Builds the script instance.

        :param build_ui: If True, UI components will be built
        :param default_values: If True, default values of the ui components will be used instead of existing values
        :param timezone: Timezone to use for time data        
        """
        if self.source.root_element_config is None:
            return
        self.setup_values(self.source.root_element_config, timezone=timezone, default_values=default_values)
        if build_ui:
            await self.build_elements(self.source.root_element_config)

    def setup_values(self, root_element: ScriptElementConfig, *, timezone: str | None, default_values: bool = False) -> None:
        """
        Sets up the values for the script instance.

        :param root_element: Root element of the script
        :param timezone: Timezone to use for time data
        :param default_values: If True, default values of the ui components will be used instead of existing values
        """
        self.update_time_data(timezone)
        for element in root_element.elements:
            if hasattr(element, 'value') and element.name and len(element.name) > 0:
                if element.name not in self.values or default_values:
                    self.values[element.name] = element.value
                if element.description:
                    self.value_descriptions[element.name] = element.description
            if element.elements:
                self.setup_values(element)

    async def build_elements(self, root: ScriptElementConfig | None) -> ui.element | None:
        for element in root.elements:
            cur_cls = NiceScript.ELEMENT_CLASSES.get(element.etype)
            if cur_cls is None:
                continue
            new_ui_element = await element.build(values=self.values)
            if element.elements:
                with new_ui_element:
                    await self.build_elements(element)        


class NiceScript:
    """Helps loading NiceGUI layouts from a script file"""

    ELEMENT_CLASSES: dict[str, type[ScriptElementConfig]] = {
        "ui.element": ScriptElementConfig,
        "ui.select": ScriptUISelectConfig            
    }

    def __init__(self, source: dict | None = None):
        self.root_element_config: ScriptElementConfig | None = None 
        self.config: NiceScriptSource = NiceScriptSource()
        if source:
            self.root_element_config = self.create_element_from_dict(source)

    @property    
    def has_elements(self) -> bool:
        """Returns True if the script has uielements, False otherwise."""
        return self.root_element_config is not None and len(self.root_element_config.elements) > 0

    @classmethod
    def create_element_from_dict(cls, data: dict, base_class: type[BaseModel]=ScriptElementConfig) -> ScriptElementConfig:
        """
        Loads the NiceScript data from a dict.
        """
        # dict with all elements except elements
        data_wo_elements = {k: v for k, v in data.items() if k != "elements"}
        root_element = base_class.model_validate(data_wo_elements)
        root_element.elements = []
        for item in data.get("elements", []):
            element_type = item.get("etype")
            if element_type in cls.ELEMENT_CLASSES:
                root_element.elements.append(cls.create_element_from_dict(item, cls.ELEMENT_CLASSES[element_type]))
            else:
                raise ValueError(f"Unknown element type: {element_type}")
        return root_element

    async def build(self, values: dict[str, any] | None = None) -> NiceScriptInstance:
        instance = NiceScriptInstance(values=values, source=self)
        await instance.build()
        return instance