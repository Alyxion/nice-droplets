from abc import ABC, abstractmethod
from threading import Event
from typing import Any, Generic, TypeVar

class Task:
    """Base class for asynchronous tasks.
    
    This class provides the foundation for executing tasks that may take time and need to be cancellable on a finer level. 
    It is thread-safe and can be polled for results.

    You need to implement either execute or execute_async, depending on your needs.
    """
    def __init__(self):
        self._cancel_event = Event()
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
        """Check if the task has completed (successfully or with error). Is also set if a cancellation was requested and the task finished executing."""
        return self._is_done.is_set()      
    
    @property
    def has_error(self) -> bool:
        """Check if the task completed with an error."""
        return self._error is not None
    
    @property
    def error(self) -> Exception | None:
        """Get the error if the task failed, None otherwise."""
        return self._error
    
    def cancel(self) -> None:
        """Request cancellation of the task."""
        self._cancel_event.set()

    @property
    def is_async(self) -> bool:
        """Check if the task is executed asynchronously."""
        # Check if execute_async was overridden by comparing function objects
        if self.execute_async.__func__ != Task.execute_async:
            return True
        # Check if execute was overridden by comparing function objects
        if self.execute.__func__ != Task.execute:
            return False
        return False
    
    def run(self) -> None:
        """Run the task and store its result or error."""
        try:
            if not self.is_cancelled:
                self.execute()
        except Exception as e:
            self._error = e
        finally:
            self._is_done.set()

    async def run_async(self) -> None:
        """Run the task asynchronously and store its result or error."""
        try:
            if not self.is_cancelled:
                await self.execute_async()
        except Exception as e:
            self._error = e
        finally:
            self._is_done.set()
