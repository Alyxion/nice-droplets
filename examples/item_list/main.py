from nicegui import ui

from nice_droplets.elements.item import Item
from nice_droplets.elements.itemlist import ItemList


@ui.page('/')
def main():
    with ui.row().classes('w-full items-start gap-4'):
        # Basic list
        with ui.card().classes('w-80'):
            ui.label('Basic List').classes('text-h6 q-pa-md')
            with ItemList(bordered=True):
                item = Item()
                with item:
                    with item.add_section():
                        ui.label('Single line item')
                        
                item = Item()
                with item:
                    with item.add_section():
                        ui.label('Item with caption')
                        ui.label('Caption').classes('text-caption')
                
                ui.separator()
                        
                item = Item()
                with item:
                    with item.add_section():
                        ui.label('OVERLINE').classes('text-overline')
                        ui.label('Item with overline')
                        
        # List with icons and avatars
        with ui.card().classes('w-80'):
            ui.label('Icons & Avatars').classes('text-h6 q-pa-md')
            with ItemList(bordered=True):
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        ui.avatar(color='primary', icon='bluetooth')
                    with item.add_section():
                        ui.label('Icon as avatar')
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        ui.avatar(color='teal', text_color='white', icon='bluetooth')
                    with item.add_section():
                        ui.label('Avatar-type icon')
                
                ui.separator()
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        ui.avatar(color='purple', text_color='white', icon='bluetooth', rounded=True)
                    with item.add_section():
                        ui.label('Rounded avatar-type icon')
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        with ui.avatar(color='primary', text_color='white'):
                            ui.label('R')
                    with item.add_section():
                        ui.label('Letter avatar-type')
                
                ui.separator()
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        with ui.avatar():
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with item.add_section():
                        ui.label('Image avatar')
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        with ui.avatar(square=True):
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with item.add_section():
                        ui.label('Image square avatar')
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        with ui.avatar(rounded=True):
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with item.add_section():
                        ui.label('Image rounded avatar')
                
                ui.separator()
                        
                item = Item()
                with item:
                    with item.add_section(avatar=True):
                        with ui.avatar(rounded=True):
                            ui.image('https://cdn.quasar.dev/img/mountains.jpg')
                    with item.add_section():
                        ui.label('List item')
                        
                item = Item()
                with item:
                    with item.add_section(thumbnail=True):
                        ui.image('https://cdn.quasar.dev/img/mountains.jpg')
                    with item.add_section():
                        ui.label('List item')


ui.run()
