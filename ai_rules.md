This is a NiceGUI extension project.

Apply the following rules:
* It is a collection of components that extend the functionality of NiceGUI.
* You run all examples and test using poetry.
* If you modified a file in this project you do not need to run the current example again because it will be automatically reloaded.
  * Do not propose running the example again except I explicitly ask you to do so.
* You can usually track errors in the log terminal.
* Sometimes you forget to close a process. If you in the NiceGUI context face a `[Errno 98] Address already in use` error then execute `fuser -k 8080/tcp` to kill the process.
  * Do not kill the process if you just changed a file.

## Project structure
* The project dependencies are stored in the `pyproject.toml` file.
* The project source code is stored in the `nice_droplets` folder.
* Examples are stored in the `examples` folder. They are usually named `main.py` and each sample has its own folder.
* Tests are stored in the `tests` folder.
* New visual elements or files directly associated with these should be stored in the `elements` folder.

## Basic rules about building apps with NiceGUI

* The `ui` module is the entry point for building UIs, it contains all the basic elements.
* The `ui.page` element is the entry point for building UIs. In sample app the method `@ui.page` is used to define the main page, the method is named index.
* The most important layouting elements are `ui.row` and `ui.column` to create a row or column of elements.
* `ui.grid` can be used to create a grid of elements.
* Use the `ui.element` element to create custom elements.
* To add views nested within a view, you need to use the with statement to enter the context of the parent view.
    * Views created within the context of the parent view are nested within the parent view.
    * Views created outside the context of the parent view are not nested within the parent view.    
* To clear a view you can use an element's clear method.
* A views style can be altered using an element's style method.
* A views class can be altered using an element's classes method, Tailwind classes can be used here.
* NiceGUI is based upon Quasar and Vue, so you can use all the Quasar and Vue features.
* NiceGUI often does not implement all the features of Quasar and Vue, but you can find out which ones are missing by looking at the Quasar and Vue documentation and make use of ondocumented properties and methods.

# Example app

```python
from nicegui import ui

@ui.page('/')  # this is cruicial and usually defines the main page
async def index():
    ui.label('Hello World')
    with ui.row() as row: # horizontal row
        ui.label('Hello World')  # nested within the row
        ui.label('Hello World')
    with ui.column() as col: # vertical column
        ui.label('Hello World')  # nested within the column
        ui.label('Hello World')  
    ui.label('Hello World')  # not nested within any row or column
    ui.label('Hello World')
    def toggle_content():
        row.clear()
        with row:
            ui.label('Hello World')
            ui.label('Hello World')
    ui.button('Toggle content', on_click=toggle_content)

ui.run()
```

# Custom components

* The `ui.element` element can be used to create custom elements.
* A new element can consist just of a Python file or a Python file and a js file. The naming scheme is `<name>.py` or `<name>.py` and `<name>.js`.

## Example for a Python only component

```python
from nicegui import ui

class MyElement(ui.element):
    def __init__(self):
        super().__init__("div")
```

## Example for a Python and JS component

### Python

```python
from nicegui import ui

class MyElement(ui.element, component="my_element.js"):
    def __init__(self):
        super().__init__()
        self._props['message'] = "Hello World"        

    def say_hello(self):
        self.run_method('sayHello')
        
```

### JS for Qusar

```js
export default {
    template: `
        <div>
            <p>{{ message }}</p>
        </div>
    `,
    props: {
        message: String
    },
    mounted() {
        console.log('Mounted')
    },
    updated() {
        console.log('Updated')
    },
    beforeUnmount() {
        console.log('Before unmount')
    },
    unmounted() {
        console.log('Unmounted')
    }
    methods: {
        sayHello() {
            console.log('Hello')
        }
    }
}
```

### Events

* New events are usually dataclasses based upon either `UiEventArguments` or `EventArguments`.
* From a custom component such an event is triggered via handle_event passing the handler to be triggered and an instance of the event arguments.
* Every event needs to be able to have one or more handlers.
* The list of handlers of each type have a list of the form `self._show_handlers = [on_show] if on_show else []`.
* The most important handlers can be passed in the arguments like `on_show: Handler[ShowPopoverEventArguments] | None = None`.
* After creation a handler can be added to the list of handlers like in this example `on_show(self, handler: Handler[ShowPopoverEventArguments]) -> Self:` which adds the handler to the list of handlers.

```
@dataclass(**KWONLY_SLOTS)
class MyEventArguments(UiEventArguments):
    message: str
```

## Coding rules

* Do not use Python template classes.
* Do not use ABC.

## Testing rules

1. Always use the Screen fixture for UI components and open the screen before assertions:
   ```python
   def test_component(screen: Screen):
       component = MyComponent()
       screen.open('/')
       # assertions
   ```
2. Create UI elements within a proper context using `with ui.element():` when needed:
   ```python
   with ui.element():
       component = MyComponent()
   ```
3. Test initialization with default and custom parameters to verify proper setup
4. For visual elements, use screen.should_contain() and screen.should_not_contain() to verify content:
   ```python
   screen.should_contain('Expected Text')
   screen.should_not_contain('Unwanted Text')
   ```
5. Add screen.wait() after UI updates to allow for rendering:
   ```python
   component.update()
   screen.wait(0.5)  # Wait for UI update
   ```
6. Test event handlers by creating mock callbacks and verifying they're called correctly:
   ```python
   clicked_item = None
   def on_click(e):
       nonlocal clicked_item
       clicked_item = e.item
   ```
7. For async components, use @pytest.mark.asyncio and await async operations:
   ```python
   @pytest.mark.asyncio
   async def test_async_component():
       await component.async_operation()
   ```

   Use async tests only as last resort, usually you can write NiceGUI tests in a synchronous way.
8. Test both success and error cases, including edge cases and invalid inputs
9. Use fixtures for common test data and mock objects to keep tests DRY
10. Test UI interactions using screen.click() or mock events:
    ```python
    screen.click('Button Text')
    # or
    component._handle_key(MockEventArguments('Enter'))
    ```
11. Group related tests logically and provide clear docstrings explaining test purpose
12. Test component state changes and verify they're reflected in the UI
13. For factories/builders, test all supported creation patterns and configurations
14. Mock external dependencies using pytest fixtures or unittest.mock
15. Follow the pattern: arrange (setup) → act (perform action) → assert (verify result)
