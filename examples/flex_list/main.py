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
            'label': 'Icon Avatar',
            'subtitle': 'Using icon with colors',
            'value': 100,
            'icon': 'star',
            'avatar_color': 'primary',
            'avatar_text_color': 'white',
            'stamp': '5 mins ago'
        },
        {
            'label': 'Disabled Item',
            'subtitle': 'Disabled item example',
            'value': 200,
            'icon': 'warning',
            'avatar_color': 'warning',
            'avatar_text_color': 'white',
            'disabled': True,
            'stamp': '1 hour ago'
        },
        {
            'label': 'Square Avatar',
            'subtitle': 'Square image avatar',
            'value': 300,
            'avatar': 'https://cdn.quasar.dev/img/boy-avatar.png',
            'avatar_square': True,
            'stamp': 'yesterday'
        },
        {
            'label': 'Rounded Avatar',
            'subtitle': 'Rounded image avatar',
            'value': 400,
            'avatar': 'https://cdn.quasar.dev/img/mountains.jpg',
            'avatar_rounded': True,
            'stamp': '2 days ago'
        },
        {
            'label': 'Letter Avatar',
            'subtitle': 'Using text in avatar',
            'value': 500,
            'icon': 'A',
            'avatar_color': 'purple',
            'avatar_text_color': 'white',
            'avatar_rounded': True,
            'stamp': '1 week ago'
        }
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
            def on_simple_click(e):
                ui.notify(f'Clicked: {e.item}')
            FlexList(
                items=simple_items,
                factory=DefaultFactory(),
                on_item_clicked=on_simple_click,
            ).on('select', lambda e: on_select(e.args['index'], simple_items, 'default'))

        # List view with dictionary items
        with ui.column().classes('flex-1'):
            ui.label('Item List View (Rich Items)').classes('text-lg font-bold mb-2')
            def on_dict_click(e):
                subtitle = e.item.get('subtitle', '')
                stamp = e.item.get('stamp', '')
                msg = f'Clicked: {e.item["label"]}'
                if subtitle:
                    msg += f' ({subtitle})'
                if stamp:
                    msg += f' - {stamp}'
                ui.notify(msg, color='primary')
            FlexList(
                items=dict_items,
                factory=ItemListFactory(bordered=True),
                on_item_clicked=on_dict_click,
            ).on('select', lambda e: on_select(e.args['index'], dict_items, 'list'))

    with ui.row().classes('w-full gap-4 p-4'):
        # Default view with dataclass items
        with ui.column().classes('flex-1'):
            ui.label('Default View (Dataclass Items)').classes('text-lg font-bold mb-2')
            def on_person_click(e):
                ui.notify(f'Clicked: {e.item.name} (Age: {e.item.age})', color='info')
            FlexList(
                items=person_items,
                factory=DefaultFactory(),
                on_item_clicked=on_person_click,
            ).on('select', lambda e: on_select(e.args['index'], person_items, 'person'))

        # Table view with dictionary items
        with ui.column().classes('flex-1'):
            ui.label('Table View (Dictionary Items)').classes('text-lg font-bold mb-2')
            def on_table_click(e):
                msg = f'Clicked: {e.item["name"]} - Status: {e.item["status"]}, Priority: {e.item["priority"]}'
                ui.notify(msg, color='secondary')
            FlexList(
                items=table_items,
                factory=TableItemFactory(),
                on_item_clicked=on_table_click,
            ).on('select', lambda e: on_select(e.args['index'], table_items, 'table'))


ui.run()
