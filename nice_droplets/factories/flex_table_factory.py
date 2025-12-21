from typing import Any, Optional, Callable

from nicegui import ui

from .flex_list_factory import FlexListFactory

class FlexTableFactory(FlexListFactory, short_name="Table"):
    """Factory for creating table-based lists with structured data."""
    
    def __init__(self, *, columns: list[str | dict] | None = None,
                 row_key: str = 'id',
                 **kwargs):
        """Initialize the table factory.

        :param columns: Optional list of column definitions. Each element can be either:
                     - A string (field name, auto-converts to title case for label)
                     - A dictionary with 'name', 'label', 'field' keys
        :param row_key: Name of the column containing unique data identifying the row
        """
        super().__init__(**kwargs)
        self._table = None
        self._columns = columns
        self._row_key = row_key
        self._rows = []
        
    def create_container(self) -> ui.element:
        self._container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')
        return self._container
    
    def create_item(self, data: Any) -> ui.element:
        # Items are handled in update_items
        return None

    def select_item(self, index: int) -> None:
        if self._table:
            if self._index < 0:
                self._table.selected = []
            else:
                self._table.selected = [self._items[self._index]]
    
    def deselect_item(self, index: int) -> None:
        if self._table:
            self._table.selected = []
            
    def clear(self) -> None:
        super().clear()
        self._container.clear()
        self._table = None

    def item_to_dict(self, item: Any) -> dict:
        if isinstance(item, dict):
            return item
        elif hasattr(item, 'to_dict'):
            return item.to_dict()
        else:
            raise TypeError('item must be a dict or dataclass object')
            
    def update_items(self, items: list[Any]) -> None:
        """Update displayed items in table format"""
        self.clear()
        self._items = items
        
        if not items:
            return

        if isinstance(items[0], dict):
            items = [item.copy() for item in items]
        else:
            items = [item.to_dict() for item in items]
        rows = [{key: value for key, value in item.items() if not key.startswith('_')} for item in items]

        # Use provided columns or extract from first item
        if self._columns:
            columns = []
            for col in self._columns:
                if isinstance(col, str):
                    columns.append({
                        'name': col,
                        'label': col.title(),
                        'field': col
                    })
                else:
                    columns.append(col)
        else:
            # Extract columns from the first row
            columns = [
                {'name': key, 'label': key.title(), 'field': key}
                for key in rows[0].keys() if not key.startswith('_')
            ]

        # add invisible key column to every row
        for index, row in enumerate(rows):
            row['_index'] = index

        self.rows = rows
            
        # Create table with rows and columns
        with self._container:
            self._table = ui.table(
                columns=columns,
                row_key=self._row_key,
                rows=rows,                
            )
            
        # Handle row clicks
        def on_row_click(e: Any) -> None:
            if len(e.args) < 2:
                return
            element = e.args[1]
            if not "_index" in element:
                return
            row_index = element['_index']                
            if not self.is_item_disabled(row_index):
                self.handle_item_click(row_index)
    
        self._table.on('row-click', on_row_click)
