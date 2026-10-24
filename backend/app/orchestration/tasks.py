from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    run: Callable
    label: str = "Task"
    depends_on: tuple[str, ...] = ()
    timeout_seconds: float = 120
    retries: int = 0  # Provider adapters already own their request retries.


@dataclass(frozen=True)
class ExecutionPlan:
    tasks: tuple[TaskSpec, ...]
    max_concurrency: int = 1
    timeout_seconds: float = 900
