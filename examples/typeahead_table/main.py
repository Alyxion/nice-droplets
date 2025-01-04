from nicegui import ui
import nice_droplets.dui as dui
from nice_droplets.elements.flex_list_factory import TableItemFactory
from nice_droplets.components.search_task import SearchTask


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

class TableSearchTask(SearchTask):

    def __init__(self, products: list[dict], query: str):
        self.products = products
        self.query = query
    
    def execute(self):
        """Search products that match the query across all fields."""
        query = self.query.lower()
        results = [
            product for product in self.products
            if any(str(value).lower().find(query) >= 0 for value in product.values())            
        ]
        self.set_results(results)
    
@ui.page('/')
def index():
    ui.markdown('## Product Search with Table View').classes('text-h5 mt-4 mb-2')
    
    table_factory = TableItemFactory()

    def create_search_task(query: str) -> TableSearchTask:
        return TableSearchTask(products, query)
    
    # Product search with table view factory
    with ui.input(label='Search products', placeholder='Type to search...') as product_input:
        with dui.typeahead(
            on_search=lambda query: TableSearchTask(products, query),
            min_chars=1,
            on_select=lambda product: product_input.set_value(product['name']),
            factory=table_factory
        ) as typeahead:
            pass

ui.run()