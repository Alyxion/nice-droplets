from nicegui import ui
from nice_droplets import dui
from nice_droplets.elements.fullscreen import Fullscreen

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
    fullscreen_handler = Fullscreen()
    fullscreen_button = ui.button(
        icon='fullscreen',
        on_click=lambda: fullscreen_handler.toggle(block_escape_key=True),
    )
    fullscreen_button.props('flat')

    # Dark mode toggle
    ui.markdown('## Fruit Search Example').classes('text-h5 mt-4 mb-2')
    
    # Simple fruit search
    with ui.input(label='Search fruits', placeholder='Type to search...') as fruit_input:
        with dui.typeahead(
            on_search=search_fruits_filter,
            min_chars=1,
            on_select=lambda fruit: fruit_input.set_value(fruit)
        ):
            pass  # Content is managed by the typeahead component

    # Show all fruits for reference
    ui.markdown('### Available Fruits:').classes('mt-4 mb-2')
    with ui.row().classes('flex-wrap gap-2'):
        for fruit in sorted(FRUITS):
            ui.badge(fruit)

ui.run()
