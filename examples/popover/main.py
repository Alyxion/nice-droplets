from nicegui import ui
from nice_droplets import dui


@ui.page('/')
async def index():
    def create_field(label):
        with ui.input(label=label):
            with dui.Popover(docking_side='top') as tt:
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

    # create some space on top
    ui.space().style('height: 200px;')
    with ui.row():
        with ui.element().style('width: 300px;'):
            pass
        with ui.element():
            create_field("Name")
            create_field("Email")
            create_field("Password")


ui.run(show=False, uvicorn_reload_includes='*.py, *.js')
