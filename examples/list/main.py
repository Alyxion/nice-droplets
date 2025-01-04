from nicegui import ui

import nice_droplets.dui as dui


@ui.page('/')
def main():
    with ui.row().classes('w-full items-start gap-4'):
        # Basic list
        with ui.card().classes('w-80'):
            ui.label('Basic List').classes('text-h6 q-pa-md')
            with dui.list(bordered=True):
                item = dui.item()
                with item:
                    with dui.item_section():
                        ui.label('Single line item')
                        
                item = dui.item()
                with item:
                    with dui.item_section():
                        ui.label('Item with caption')
                        ui.label('Caption').classes('text-caption')
                
                ui.separator()
                        
                item = dui.item()
                with item:
                    with dui.item_section():
                        ui.label('OVERLINE').classes('text-overline')
                        ui.label('Item with overline')
                        
        # List with icons and avatars
        with ui.card().classes('w-80'):
            ui.label('Icons & Avatars').classes('text-h6 q-pa-md')
            with dui.list(bordered=True):
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        ui.avatar(color='primary', icon='bluetooth')
                    with dui.item_section():
                        ui.label('Icon as avatar')
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        ui.avatar(color='teal', text_color='white', icon='bluetooth')
                    with dui.item_section():
                        ui.label('Avatar-type icon')
                
                ui.separator()
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        ui.avatar(color='purple', text_color='white', icon='bluetooth', rounded=True)
                    with dui.item_section():
                        ui.label('Rounded avatar-type icon')
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        with ui.avatar(color='primary', text_color='white'):
                            ui.label('R')
                    with dui.item_section():
                        ui.label('Letter avatar-type')
                
                ui.separator()
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        with ui.avatar():
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with dui.item_section():
                        ui.label('Image avatar')
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        with ui.avatar(square=True):
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with dui.item_section():
                        ui.label('Image square avatar')
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        with ui.avatar(rounded=True):
                            ui.image('https://cdn.quasar.dev/img/boy-avatar.png')
                    with dui.item_section():
                        ui.label('Image rounded avatar')
                
                ui.separator()
                        
                item = dui.item()
                with item:
                    with dui.item_section(avatar=True):
                        with ui.avatar(rounded=True):
                            ui.image('https://cdn.quasar.dev/img/mountains.jpg')
                    with dui.item_section():
                        ui.label('Image rounded mountains avatar')
                        ui.label('With caption').classes('text-caption')


ui.run()
