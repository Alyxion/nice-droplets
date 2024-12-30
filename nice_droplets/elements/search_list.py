from typing import Any, Callable, TypeVar
from nicegui import ui
from nicegui.events import ValueChangeEventArguments, GenericEventArguments, Handler, handle_event

from nice_droplets.components import SearchTask
from nice_droplets.components.task_executor import TaskExecutor
from nice_droplets.events import SearchListContentUpdateEventArguments

T = TypeVar('T')

class SearchList(ui.element):
    """List component showing search results with keyboard navigation"""

    def __init__(self,
                 *,
                 on_search: Callable[[str], SearchTask] | None = None,
                 min_chars: int = 1,
                 debounce: float = 0.3,
                 item_label: Callable[[Any], str] | None = None,
                 on_select: Callable[[Any], None] | None = None,
                 on_content_update: Handler[SearchListContentUpdateEventArguments] | None = None,
                 poll_interval: float = 0.1
                 ):
        super().__init__()
        self._on_search = on_search
        self._min_chars = min_chars
        self._item_label = item_label or str
        self._on_select = on_select
        self._content_update_handlers = [on_content_update] if on_content_update else []
        self._poll_interval = poll_interval
        self._items: list[Any] = []
        self._suggestion_elements: list[ui.element] = []
        self._selected_index = -1
        self._task_executor = TaskExecutor(debounce)
        self._poll_timer: ui.timer | None = None

        with self:
            self._suggestions_container = ui.element('div').classes('flex flex-col gap-1 min-w-[200px]')

    def on_content_update(self, handler: Handler[SearchListContentUpdateEventArguments]) -> None:
        """Add content update handler"""
        self._content_update_handlers.append(handler)

    @property
    def items(self) -> list[Any]:
        return self._items

    def _update_selection(self) -> None:
        """Update visual selection"""
        for i, item_element in enumerate(self._suggestion_elements):
            if i == self._selected_index:
                item_element.classes('bg-primary text-white', remove='hover:bg-gray-100')
            else:
                item_element.classes('hover:bg-gray-100', remove='bg-primary text-white')                

    def clear(self) -> None:
        """Clear suggestions"""
        self._suggestions_container.clear()
        self._items = []
        self._suggestion_elements = []
        self._selected_index = -1
        self._task_executor.cancel()
        if self._poll_timer:
            self._poll_timer.cancel()
            self._poll_timer = None
        self._notify_content_update()

    def update_items(self, items: list[Any]) -> None:
        """Update displayed items"""
        self.clear()
        self._items = items
        with self._suggestions_container:
            for item in items:
                label = self._item_label(item)
                item_element = ui.element('div').classes(
                    'w-full px-3 py-2 cursor-pointer hover:bg-gray-100 transition-colors'
                ).on('click', lambda i=item: self._handle_item_click(i))
                with item_element:
                    ui.label(label).classes('w-full text-left')
                self._suggestion_elements.append(item_element)
        self._notify_content_update()

    def _notify_content_update(self) -> None:
        """Notify content update handlers"""
        args = SearchListContentUpdateEventArguments(sender=self, client=self.client)
        for handler in self._content_update_handlers:
            handle_event(handler, args)

    def handle_key(self, e: GenericEventArguments) -> bool:
        """Handle keyboard navigation"""
        key = e.args.get('key', '')
        handled = True

        if key == 'ArrowDown':
            if self._selected_index < len(self._items) - 1:
                self._selected_index += 1
                self._update_selection()
        elif key == 'ArrowUp':
            if self._selected_index > 0:
                self._selected_index -= 1
                self._update_selection()
        elif key == 'Enter':
            if 0 <= self._selected_index < len(self._items):
                self._handle_item_click(self._items[self._selected_index])
        else:
            handled = False

        return handled

    def handle_input_change(self, e: ValueChangeEventArguments) -> None:
        """Handle input changes"""
        value = str(e.value or '')
        
        if len(value) < self._min_chars:
            self.clear()
            return

        if not self._on_search:
            return

        # Start new search task with debouncing
        task = self._on_search(value)
        self._task_executor.schedule(task)
        
        # Start polling for results
        if self._poll_timer:
            self._poll_timer.cancel()
        self._poll_timer = ui.timer(
            self._poll_interval,
            self._check_search_results,
            active=True
        )

    def _check_search_results(self) -> None:
        """Check if search results are ready"""
        task = self._task_executor.current_task
        if task is None:
            return
        if not task.is_done:
            return
            
        if self._poll_timer:
            self._poll_timer.cancel()
            self._poll_timer = None
            
        if task.has_error:
            print(f"Search error: {task.error}")
            self.clear()
            return
            
        results = task.result or []
        self.update_items(results)

    def _handle_item_click(self, item: Any) -> None:
        """Handle item selection"""
        if self._on_select:
            self._on_select(item)
