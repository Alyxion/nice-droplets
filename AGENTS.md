# AGENTS.md

This file provides guidance to AI coding assistants (Claude Code, Windsurf, Cursor, Copilot, etc.) when working with code in this repository.

## Project Overview

NiceDroplets is a Python library providing UI extensions and components for NiceGUI. Key features include flexible list components with factory patterns, typeahead/autocomplete, PDF viewing, and async task execution.

## Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run single test file
poetry run pytest tests/test_flex_list.py -v

# Run tests with output
poetry run pytest -xvs tests/

# Run examples (auto-reloads on file changes)
poetry run python examples/typeahead/main.py

# Kill stuck process on port 8080
fuser -k 8080/tcp
```

## Architecture

### Package Structure

- `nice_droplets/dui.py` - Main entry point exporting all UI components (lowercase aliases)
- `nice_droplets/elements/` - NiceGUI UI elements (FlexList, Typeahead, SearchList, Popover, PDF viewer)
- `nice_droplets/factories/` - Factory pattern implementations for list item rendering
- `nice_droplets/tasks/` - Async task execution system with debouncing
- `nice_droplets/components/` - Core reusable components (SearchManager, event handling)
- `nice_droplets/helpers/` - Utilities (MongoDB logging, config, security)
- `examples/` - Example applications, each in its own folder with `main.py`

### Key Patterns

**Factory Pattern for Lists**: `FlexListFactory` subclasses control item rendering. Register with `short_name` metaclass parameter:
```python
class MyFactory(FlexListFactory, short_name="MyName"):
    def create_item(self, data: Any) -> ui.element: ...
```

**Event Handling**: Dataclass-based events with handler lists:
```python
@dataclass(**KWONLY_SLOTS)
class MyEventArguments(UiEventArguments):
    item: Any

# Handlers stored as lists: self._handlers = [on_event] if on_event else []
```

**Task Execution**: `Task` and `QueryTask` for async operations, `TaskExecutor` for debouncing.

### Component Usage

```python
from nice_droplets import dui

flex_list = dui.flex_list(items=data, factory="Default")
typeahead = dui.typeahead(on_search=lambda q: QueryTask(...))
pdf_viewer = dui.pdf_viewer(pdf_path="document.pdf")
```

## Development Rules

- Hot reload is enabled - file changes auto-refresh the UI, don't restart examples manually
- Do not use ABC (Abstract Base Classes) or Python template classes
- All commands run via Poetry
- Python 3.12+ required

## NiceGUI Basics

- `ui.page` decorator defines routes; `@ui.page('/')` is the main page
- `ui.row` and `ui.column` for layout, use `with` statement for nesting
- `ui.element` base class for custom components
- NiceGUI is built on Quasar/Vue - those features are available

### Custom Components

Python-only:
```python
class MyElement(ui.element):
    def __init__(self):
        super().__init__("div")
```

Python + JavaScript:
```python
class MyElement(ui.element, component="my_element.js"):
    def __init__(self):
        super().__init__()
        self._props['message'] = "Hello"

    def say_hello(self):
        self.run_method('sayHello')
```

## Testing

Uses pytest with NiceGUI's `Screen` fixture for UI testing.

### Running Tests

```bash
# Run all tests - show full output, no tailing
poetry run pytest tests/

# Run single test file
poetry run pytest tests/test_flex_list.py

# Run specific test
poetry run pytest tests/test_flex_list.py::test_flex_list_initialization
```

**Important**: Never use `| head` or `| tail` when running tests. Always show full output so progress can be monitored.

### Test Structure

NiceGUI UI tests must create elements inside a `@ui.page` decorator:

```python
def test_component(screen: Screen):
    refs = []

    @ui.page('/')
    def page():
        component = MyComponent()
        refs.append(component)

    screen.open('/')
    screen.wait(0.3)

    component = refs[0]
    assert component.value == expected
    screen.should_contain('Expected Text')
```

### Guidelines

- All UI elements must be created inside `@ui.page` function
- Use `refs` list to pass component references out of page function
- `screen.wait(0.3)` after `screen.open('/')` for UI initialization
- Prefer synchronous tests; use `@pytest.mark.asyncio` only when necessary
- Mock external dependencies (MongoDB tests skip when unavailable)
- Test both success and error cases
- Use `screen.click('Button Text')` for UI interactions
- Module-scoped fixtures don't work with NiceGUI Screen tests due to session invalidation
