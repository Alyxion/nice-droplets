from abc import ABC, abstractmethod
from threading import Event
from typing import Any, Generic, TypeVar

class Task:
    """Base class for asynchronous tasks.
    
    This class provides the foundation for executing tasks that may take time
    and need to be cancellable. It is thread-safe and can be polled for results.
    """
    def __init__(self):
        self._cancel_event = Event()
        self._result: Any | None = None
        self._is_done = Event()
        self._error: Exception | None = None

    def execute(self):
        """Execute the task. Must be implemented by subclasses.
        
        This method should periodically check self.is_cancelled and return early if true.
        """
        raise NotImplementedError()

    async def execute_async(self):
        """Execute the task asynchronously. Must be implemented by subclasses.
        
        This method should periodically check self.is_cancelled and return early if true.
        """
        raise NotImplementedError()

    @property
    def is_cancelled(self) -> bool:
        """Check if the task has been cancelled."""
        return self._cancel_event.is_set()
    
    @property
    def is_done(self) -> bool:
        """Check if the task has completed (successfully or with error)."""
        return self._is_done.is_set()
    
    @property
    def has_error(self) -> bool:
        """Check if the task completed with an error."""
        return self._error is not None
    
    @property
    def error(self) -> Exception | None:
        """Get the error if the task failed, None otherwise."""
        return self._error
    
    @property
    def result(self):
        """Get the result of the task if available, None otherwise."""
        return self._result
    
    def cancel(self) -> None:
        """Request cancellation of the task."""
        self._cancel_event.set()
    
    def run(self) -> None:
        """Run the task and store its result or error."""
        try:
            if not self.is_cancelled:
                self._result = self.execute()
        except Exception as e:
            self._error = e
        finally:
            self._is_done.set()

    async def run_async(self) -> None:
        """Run the task asynchronously and store its result or error."""
        try:
            if not self.is_cancelled:
                self._result = await self.execute_async()
        except Exception as e:
            self._error = e
        finally:
            self._is_done.set()
