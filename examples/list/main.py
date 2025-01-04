from nicegui import ui

import nice_droplets.dui as dui


@ui.page('/')
def main():
    with ui.element('div').classes('q-pa-md w-[350px]'):
        with dui.list(bordered=True, padding=True):
            # Basic item with multiple labels
            with dui.item():
                with dui.item_section():
                    dui.item_label('OVERLINE', overline=True)
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True)
                with dui.item_section(side=True, top=True):
                    dui.item_label('5 min ago', caption=True)

            ui.separator().classes('q-my-sm')
            dui.item_label('List Header', header=True)

            # Item with icon
            with dui.item():
                with dui.item_section(avatar=True):
                    ui.icon('bluetooth', color='primary')
                with dui.item_section():
                    dui.item_label('List item')
                with dui.item_section(side=True):
                    dui.item_label('meta', caption=True)

            ui.separator().classes('q-my-sm q-ml-[56px]')

            # Item with avatar and multiple sections
            with dui.item():
                with dui.item_section(top=True, avatar=True):
                    ui.avatar(color='primary', text_color='white', icon='bluetooth')
                with dui.item_section():
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True, lines=2)
                with dui.item_section(side=True, top=True):
                    dui.item_label('5 min ago', caption=True)
                    ui.icon('star', color='yellow')

            ui.separator().classes('q-my-sm q-ml-[56px]')

            # Item with square avatar
            with dui.item():
                with dui.item_section(top=True, avatar=True):
                    ui.avatar(color='primary', text_color='white', icon='bluetooth', square=True)
                with dui.item_section():
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True)
                with dui.item_section(side=True, top=True):
                    dui.item_label('meta', caption=True)

            ui.separator().classes('q-my-sm q-ml-[56px]')

            # Item with image avatar
            with dui.item():
                with dui.item_section(top=True, avatar=True):
                    ui.avatar('img:https://cdn.quasar.dev/img/boy-avatar.png')
                with dui.item_section():
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True)
                with dui.item_section(side=True, top=True):
                    ui.badge('10k')

            ui.separator().classes('q-my-sm q-ml-[56px]')

            # Item with rounded image avatar
            with dui.item():
                with dui.item_section(top=True, avatar=True):
                    ui.avatar('img:https://cdn.quasar.dev/img/boy-avatar.png', rounded=True)
                with dui.item_section():
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True)
                with dui.item_section(side=True, top=True):
                    dui.item_label('meta', caption=True)

            ui.separator().classes('q-my-sm')

            # Item with thumbnail
            with dui.item():
                with dui.item_section(top=True, thumbnail=True).classes('q-ml-none'):
                    ui.html('<img src="https://cdn.quasar.dev/img/mountains.jpg" />')
                with dui.item_section():
                    dui.item_label('Single line item')
                    dui.item_label('Secondary line text. Lorem ipsum dolor sit amet, consectetur adipiscit elit.', caption=True)
                with dui.item_section(side=True, top=True):
                    dui.item_label('meta', caption=True)


ui.run()
