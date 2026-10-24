"""Shared, synchronous agent contract with cooperative task cancellation."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.orchestration.runtime import check_active
from app.orchestration.agent_activity import agent_activity

Result = TypeVar("Result")


class BaseAgent(ABC, Generic[Result]):
    """Implement _run; keep provider dependencies injected and results request-local."""


    def run(self, *args, **kwargs) -> Result:
        check_active()
        with agent_activity(type(self).__name__):
            result = self._run(*args, **kwargs)
            check_active()
            return result


    @abstractmethod
    def _run(self, *args, **kwargs) -> Result:
        """Execute a task or raise; never return a successful partial result."""
