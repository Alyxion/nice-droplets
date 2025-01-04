from dataclasses import dataclass
from typing import Any

from nicegui import ui

from nice_droplets.elements.flex_list import FlexList
from nice_droplets.elements.flex_list_factory import DefaultFactory, ItemListFactory, TableItemFactory


@dataclass
class Person:
    name: str
    age: int
    disabled: bool = False


@ui.page('/')
async def main():
    ui.label('FlexList Examples').classes('text-2xl font-bold mb-4')
    
    # Sample data
    simple_items = ['Item 1', 'Item 2', 'Item 3 (Disabled)', 'Item 4', 'Item 5']
    dict_items = [
        {
            'label': 'First Item',
            'subtitle': 'This is a subtitle',
            'value': 100,
            'icon': 'star',
            'stamp': '5 mins ago'
        },
        {
            'label': 'Second Item',
            'subtitle': 'Disabled item example',
            'value': 200,
            'icon': 'warning',
            'disabled': True,
            'stamp': '1 hour ago'
        },
        {
            'label': 'Third Item',
            'subtitle': 'With avatar instead of icon',
            'value': 300,
            'avatar': 'https://avatars.githubusercontent.com/u/1',
            'stamp': 'yesterday'
        },
    ]
    person_items = [
        Person('Alice', 25),
        Person('Bob', 30, disabled=True),
        Person('Charlie', 35),
    ]
    table_items = [
        {'name': 'Project A', 'status': 'Active', 'priority': 'High'},
        {'name': 'Project B', 'status': 'On Hold', 'priority': 'Medium', 'disabled': True},
        {'name': 'Project C', 'status': 'Completed', 'priority': 'Low'},
    ]

    def on_select(index: int, items: list[Any], list_type: str) -> None:
        item = items[index]
        if isinstance(item, dict):
            label = item.get('label', str(item))
        else:
            label = str(item)
        ui.notify(f'Selected {label} in {list_type} list')

    with ui.row().classes('w-full gap-4 p-4'):
        # Default view with simple items
        with ui.column().classes('flex-1'):
            ui.label('Default View (Simple Items)').classes('text-lg font-bold mb-2')
            FlexList(
                items=simple_items,
                factory=DefaultFactory(),
            ).on('select', lambda e: on_select(e.args['index'], simple_items, 'default'))

        # List view with dictionary items
        with ui.column().classes('flex-1'):
            ui.label('Item List View (Rich Items)').classes('text-lg font-bold mb-2')
            FlexList(
                items=dict_items,
                factory=ItemListFactory(),
            ).on('select', lambda e: on_select(e.args['index'], dict_items, 'list'))

    with ui.row().classes('w-full gap-4 p-4'):
        # Default view with dataclass items
        with ui.column().classes('flex-1'):
            ui.label('Default View (Dataclass Items)').classes('text-lg font-bold mb-2')
            FlexList(
                items=person_items,
                factory=DefaultFactory(),
            ).on('select', lambda e: on_select(e.args['index'], person_items, 'person'))

        # Table view with dictionary items
        with ui.column().classes('flex-1'):
            ui.label('Table View (Dictionary Items)').classes('text-lg font-bold mb-2')
            FlexList(
                items=table_items,
                factory=TableItemFactory(),
            ).on('select', lambda e: on_select(e.args['index'], table_items, 'table'))


ui.run()
