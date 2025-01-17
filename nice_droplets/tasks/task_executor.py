import asyncio
from typing import Generic, TypeVar
from threading import Thread
from nicegui import background_tasks, ui, run

from .task import Task

class TaskExecutor:
    """Executes tasks with debouncing"""

    def __init__(self, debounce: float = 0.3, max_pending_tasks: int = 2):
        self._debounce = debounce
        self._current_task: Task | None = None
        self._current_task_started = False
        self._previous_tasks: list[Task | None] = []
        self._max_pending_tasks = max_pending_tasks
        self._pending_tasks_sleep_interval = 0.02
        self._timer = ui.timer(
            self._debounce,
            self._execute_current_task,
            active=False,
            once=False
        )

    def schedule(self, task: Task) -> None:
        """Execute task after debounce period"""
        self.cancel()
        self._current_task = task
        self._current_task_started = False
        self._timer.interval = self._debounce
        self._timer.activate()

    def cancel(self) -> None:
        """Cancel current task"""
        self._timer.deactivate()
        if self._current_task:
            self._current_task.cancel()
            if self._current_task_started and not self._current_task.is_done:
                self._previous_tasks.append(self._current_task)
            self._current_task = None

    async def _execute_current_task(self) -> None:
        """Start task in thread or run async based on implementation"""
        while len(self._previous_tasks) >= self._max_pending_tasks:
            # sleep and wait for more tasks to be executed
            await asyncio.sleep(self._pending_tasks_sleep_interval)
            for task in self._previous_tasks:
                if task.is_done:
                    self._previous_tasks.remove(task)
                    break
        if self._current_task:
            self._current_task_started = True
            # Check if execute_async is overridden
            if self._current_task.is_async:
                background_tasks.create(self._current_task._run_async())
            else:
                run.thread_pool.submit(self._current_task._run)

    @property
    def current_task(self) -> Task | None:
        """The currently scheduled or running task"""
        return self._current_task

    @property
    def debounce(self) -> float:
        """The debounce time in seconds"""
        return self._debounce

    @debounce.setter
    def debounce(self, value: float) -> None:
        """Set a new debounce time"""
        self._debounce = value
