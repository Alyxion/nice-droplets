from nicegui import ui
import nice_droplets.dui as dui
from nice_droplets.factories import FlexTableFactory
from nice_droplets.tasks.query_task import QueryTask


# Sample data with more structured information
products = [
    {'id': 1, 'name': 'Apple MacBook Pro', 'category': 'Laptops', 'price': 1299.99, 'stock': 50},
    {'id': 2, 'name': 'Dell XPS 13', 'category': 'Laptops', 'price': 999.99, 'stock': 30},
    {'id': 3, 'name': 'iPhone 13', 'category': 'Phones', 'price': 799.99, 'stock': 100},
    {'id': 4, 'name': 'Samsung Galaxy S21', 'category': 'Phones', 'price': 699.99, 'stock': 75},
    {'id': 5, 'name': 'iPad Pro', 'category': 'Tablets', 'price': 899.99, 'stock': 40},
    {'id': 6, 'name': 'Samsung Galaxy Tab S7', 'category': 'Tablets', 'price': 649.99, 'stock': 25},
    {'id': 7, 'name': 'AirPods Pro', 'category': 'Audio', 'price': 249.99, 'stock': 200},
    {'id': 8, 'name': 'Sony WH-1000XM4', 'category': 'Audio', 'price': 349.99, 'stock': 60},
    {'id': 9, 'name': 'Apple Watch Series 7', 'category': 'Wearables', 'price': 399.99, 'stock': 80},
    {'id': 10, 'name': 'Samsung Galaxy Watch 4', 'category': 'Wearables', 'price': 249.99, 'stock': 45},
]

class TableSearchTask(QueryTask):

    def __init__(self, products: list[dict], query: str, field: str = 'name'):
        super().__init__()
        self.products = products
        self.query = query
        self.field = field
    
    def execute(self):
        """Search products that match the query across all fields."""
        query = self.query.lower()
        results = [
            product for product in self.products
            if query in product[self.field].lower()
        ]
        self.set_elements(results)
    
@ui.page('/')
def index():
    ui.markdown('## Product Search with Table View').classes('text-h5 mt-4 mb-2')
    
    def create_search_task(query: str, field: str) -> TableSearchTask:
        return TableSearchTask(products, query, field)
    
    # Create a grid for product fields
    with ui.grid(columns=2).classes('w-96 gap-4'):
        # Product name field
        with ui.input(label='Product Name') as name_input:
            typeahead = dui.typeahead(
                on_value_select=lambda e: e.item['name'],
                on_search=lambda query: create_search_task(query, 'name'),
                min_chars=1,
                factory=FlexTableFactory()
            )
        
        # Product category field
        category_input = ui.input(label='Category')
        typeahead.observe(category_input, on_value_select=lambda e: e.item['category'], on_search=lambda query: create_search_task(query, 'category'))
        
        # Product price field
        price_input = ui.input(label='Price')
        typeahead.observe(price_input, on_value_select=lambda e: f"${e.item['price']}", on_search=lambda query: create_search_task(query, 'price'))
        
        # Product stock field
        stock_input = ui.input(label='Stock')
        typeahead.observe(stock_input, on_value_select=lambda e: str(e.item['stock']), on_search=lambda query: create_search_task(query, 'stock'))
        
        # Update all fields when any field is selected
        def update_all_fields(e):
            name_input.value = e.item['name']
            category_input.value = e.item['category']
            price_input.value = f"${e.item['price']}"
            stock_input.value = str(e.item['stock'])
        
        typeahead.on_value_select = update_all_fields

ui.run()
