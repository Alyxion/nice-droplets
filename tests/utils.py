from nice_droplets.tasks.task import Task


class MockTaskExecutor:
    """A simplified TaskExecutor for testing that doesn't use NiceGUI timer."""
    def __init__(self, debounce: float = 0):
        self._current_task: Task | None = None

    def schedule(self, task: Task) -> None:
        self._current_task = task

    def cancel(self) -> None:
        if self._current_task:
            self._current_task.cancel()
            self._current_task = None

    async def _execute_current_task(self) -> None:
        if self._current_task:
            if self._current_task.is_async:
                await self._current_task._run_async()
            else:
                self._current_task._run()

    @property
    def current_task(self) -> Task | None:
        return self._current_task
