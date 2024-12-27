from xml.dom.minidom import Element

from nicegui import ui
from nice_droplets import dui


@ui.page('/')
async def index():
    def create_field(label):
        with ui.input(label=label) as input:
            pass

            with dui.Popover() as tt:
                tt.style('background-color: white;')
                # tt.observe(input)
                # a small table with some suggestions
                rows = [
                    {'name': 'Elsa', 'age': 18},
                    {'name': 'Oaken', 'age': 46},
                    {'name': 'Hans', 'age': 20},
                    {'name': 'Sven'},
                    {'name': 'Olaf', 'age': 4},
                    {'name': 'Anna', 'age': 17},
                ]
                ui.table(rows=rows, column_defaults={'sortable': False},
                         columns=[{'name': 'name', 'label': 'Name', 'field': 'name'},
                                  {'name': 'age', 'label': 'Age', 'field': 'age'}])

    create_field("Name")
    create_field("Email")
    create_field("Password")


ui.run(show=False)
