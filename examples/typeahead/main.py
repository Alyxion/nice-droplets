from nicegui import ui
import nice_droplets.dui as dui
from nice_droplets.tasks.query_task import QueryTask

FRUITS = [
    'Apple', 'Apricot', 'Avocado',
    'Banana', 'Blackberry', 'Blueberry',
    'Cherry', 'Coconut', 'Cranberry',
    'Date', 'Dragon Fruit',
    'Elderberry',
    'Fig',
    'Grape', 'Grapefruit', 'Guava',
    'Kiwi', 'Kumquat',
    'Lemon', 'Lime', 'Lychee',
    'Mango', 'Melon',
    'Orange',
    'Papaya', 'Peach', 'Pear', 'Pineapple', 'Plum', 'Pomegranate',
    'Raspberry',
    'Strawberry',
    'Tangerine',
    'Watermelon'
]

async def search_fruits_filter(query: str) -> list[str]:
    """Search fruits that match the query."""
    query = query.lower()
    return [fruit for fruit in FRUITS if query in fruit.lower()]

@ui.page('/')
def index():
    # Dark mode toggle
    ui.markdown('## Fruit Search Example').classes('text-h5 mt-4 mb-2')
    
    # Simple fruit search
    with ui.input(label='Search fruits', placeholder='Type to search...') as fruit_input:
        with dui.typeahead(
            on_search=lambda query: QueryTask(search_fruits_filter, query),
            min_chars=1,
            on_click=lambda fruit: fruit_input.set_value(fruit)
        ):
            pass  # Content is managed by the typeahead component

    # Show all fruits for reference
    ui.markdown('### Available Fruits:').classes('mt-4 mb-2')
    with ui.row().classes('flex-wrap gap-2'):
        for fruit in sorted(FRUITS):
            ui.badge(fruit)

ui.run()
