import os
from dataclasses import dataclass
from datetime import datetime

from nicegui import ui

from nice_droplets import dui
from nice_droplets.factories import FlexItemListFactory, FlexListFactory

@dataclass
class Person:
    name: str
    age: int
    
    
@dataclass
class Project:
    name: str
    status: str
    priority: str
    
    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status,
            'priority': self.priority
        }

class PersonListFactory(FlexItemListFactory):
    def setup_item(self, item, data) -> ui.element:
        with item:  # add item section, avatar and text content
            with dui.item_section(avatar=True):
                ui.icon('person').classes('text-2xl')            
            with dui.item_section():
                ui.label(data.name).classes('text-h6')
                ui.label(f'{data.age} years old').classes('text-body2')

    
@ui.page('/')
def main():
    with ui.row().classes('w-full items-start gap-4'):
        # Simple items
        with ui.card().classes('w-80'):
            ui.label('Simple Items').classes('text-h6 q-pa-md')
            with dui.flex_list(factory="Default") as list:  # Using string name instead of FlexDefaultFactory()
                list.update_items([
                    'Item 1',
                    'Item 2',
                    'Item 3',
                    'Item 4',
                    'Item 5',
                ])
                
                def on_item_clicked(e) -> None:
                    ui.notify(f'Clicked item {e.item}')
                    
                list.on_click(on_item_clicked)
                
        # Rich items
        with ui.card().classes('w-80'):
            ui.label('Rich Items').classes('text-h6 q-pa-md')
            # Using string name "Item" with kwargs
            with dui.flex_list(factory=FlexListFactory.create_by_name("Item", bordered=True, separator=True, padding=True)) as list:
                list.update_items([
                    {
                        'label': 'Item 1',
                        'subtitle': 'Subtitle 1',
                        'stamp': datetime.now().strftime('%H:%M'),
                    },
                    {
                        'label': 'Item 2',
                        'subtitle': 'Subtitle 2',
                        'stamp': datetime.now().strftime('%H:%M'),
                    },
                    {
                        'label': 'Item 3',
                        'subtitle': 'Subtitle 3',
                        'stamp': datetime.now().strftime('%H:%M'),
                    },
                ])
                
                def on_item_clicked(e) -> None:
                    item = e.item
                    ui.notify(f'Clicked item {item["label"]} ({item["subtitle"]}) at {item["stamp"]}')
                    
                list.on_click(on_item_clicked)
                
        # Dataclass items
        with ui.card().classes('w-80'):
            ui.label('Dataclass Items').classes('text-h6 q-pa-md')
            with dui.flex_list(factory=PersonListFactory(bordered=True)) as list:
                list.update_items([
                    Person('John', 25),
                    Person('Jane', 30),
                    Person('Bob', 35),
                ])
                
                def on_item_clicked(e) -> None:
                    person = e.item
                    ui.notify(f'Clicked person {person.name} ({person.age} years old)')
                    
                list.on_click(on_item_clicked)
                
        # Table items
        with ui.card().classes('w-80'):
            ui.label('Table Items').classes('text-h6 q-pa-md')
            with dui.flex_list(factory="Table") as list:  # Using string name instead of FlexTableFactory()
                projects = [
                    Project('Project 1', 'In Progress', 'High'),
                    Project('Project 2', 'Done', 'Medium'),
                    Project('Project 3', 'Pending', 'Low'),
                ]
                list.update_items(projects)
                
                def on_item_clicked(e) -> None:
                    project = e.item
                    ui.notify(f'Clicked project {project.name} ({project.status}, {project.priority} priority)')
                    
                list.on_click(on_item_clicked)


ui.run(show=os.getenv('SHOW_UI', '1') == '1')
