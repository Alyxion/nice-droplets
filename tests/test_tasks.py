import asyncio
import pytest
from nicegui import ui, run
from nicegui.testing import Screen
from unittest.mock import Mock, patch

from nice_droplets.tasks.task import Task
from nice_droplets.tasks.query_task import QueryTask
from tests.utils import MockTaskExecutor


class SimpleTask(Task):
    def __init__(self):
        super().__init__()
        self.executed = False

    def execute(self):
        self.executed = True


class AsyncTask(Task):
    def __init__(self):
        super().__init__()
        self.executed = False

    async def execute_async(self):
        self.executed = True


@pytest.mark.asyncio
async def test_sync_task_execution():
    """Test synchronous task execution."""
    task = SimpleTask()
    executor = MockTaskExecutor()
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.executed
    assert task.is_done
    assert not task.has_error


@pytest.mark.asyncio
async def test_async_task_execution():
    """Test asynchronous task execution."""
    task = AsyncTask()
    executor = MockTaskExecutor()
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.executed
    assert task.is_done
    assert not task.has_error


def test_task_cancellation():
    """Test task cancellation."""
    task = SimpleTask()
    executor = MockTaskExecutor()
    executor.schedule(task)
    executor.cancel()
    assert not task.executed
    assert task.is_cancelled


@pytest.mark.asyncio
async def test_task_error_handling():
    """Test error handling in tasks."""
    class ErrorTask(Task):
        def execute(self):
            raise ValueError("Test error")

    task = ErrorTask()
    executor = MockTaskExecutor()
    executor.schedule(task)
    await executor._execute_current_task()
    assert task.is_done
    assert task.has_error
    assert isinstance(task.error, ValueError)
    assert str(task.error) == "Test error"


@pytest.mark.asyncio
async def test_task_executor():
    """Test task executor functionality."""
    executor = MockTaskExecutor()
    
    # Test scheduling
    schedule_task = SimpleTask()
    executor.schedule(schedule_task)
    assert executor.current_task == schedule_task
    assert not schedule_task.executed

    # Test cancellation
    cancel_task = SimpleTask()
    executor.schedule(cancel_task)
    executor.cancel()
    assert executor.current_task is None
    assert not cancel_task.executed

    # Test execution
    execute_task = SimpleTask()
    executor.schedule(execute_task)
    await executor._execute_current_task()
    assert execute_task.is_done
    assert execute_task.executed
