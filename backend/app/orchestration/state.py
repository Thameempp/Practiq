"""Request-local task state; the scheduler alone changes execution statuses."""

from dataclasses import dataclass, field
from threading import Event
from uuid import uuid4

TERMINAL = {"succeeded", "failed", "timed_out", "cancelled", "skipped"}


@dataclass
class TaskResult:
    task_id: str
    status: str = "pending"
    attempts: int = 0
    result: object = None
    evidence: list[dict] = field(default_factory=list)
    text: str = ""
    error: str | None = None
    deadline: float | None = None
    started_at: float | None = None
    finished_at: float | None = None


@dataclass
class WorkflowState:
    action: str
    request_id: str = field(default_factory=lambda: uuid4().hex)
    status: str = "pending"
    tasks: dict[str, TaskResult] = field(default_factory=dict)
    cancel: Event = field(default_factory=Event, repr=False)


    def finish(self):
        statuses = [task.status for task in self.tasks.values()]
        if self.cancel.is_set():
            self.status = "cancelled"
        elif statuses and all(status == "succeeded" for status in statuses):
            self.status = "succeeded"
        elif "succeeded" in statuses:
            self.status = "partial"
        else:
            self.status = "failed"


    def snapshot(self):
        return {"request_id": self.request_id, "action": self.action, "status": self.status,
                "tasks": [{"task_id": task.task_id, "status": task.status,
                           "attempts": task.attempts, "error": task.error,
                           "evidence_count": len(task.evidence),
                           "duration_seconds": (task.finished_at - task.started_at)
                           if task.started_at is not None and task.finished_at is not None else None}
                          for task in self.tasks.values()]}
