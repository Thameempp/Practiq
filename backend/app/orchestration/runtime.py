"""Cooperative cancellation at task and provider-call boundaries."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from time import monotonic
from threading import Event

from app.orchestration.errors import TaskCancelled, TaskDeadline

current_task = ContextVar("orchestration_task", default=None)


@dataclass
class TaskContext:
    deadline: float
    cancel: object
    outputs: dict
    send: object
    evidence: list[dict] = field(default_factory=list)
    published: bool = False


    def check(self):
        if self.cancel.is_set():
            raise TaskCancelled("Task cancelled.")
        if monotonic() >= self.deadline:
            raise TaskDeadline("Task exceeded its time limit.")


    def emit(self, text):
        self.check()
        if text:
            self.send("text", str(text))
            self.published = True


def check_active():
    context = current_task.get()
    if context is not None:
        context.check()


def capture_evidence(chunks):
    context = current_task.get()
    if context is not None:
        context.evidence.extend(chunks)


def report_progress(update):
    context = current_task.get()
    if context is not None:
        context.check()
        context.send("progress", update)


def request_timeout(default=60.0):
    check_active()
    context = current_task.get()
    return min(default, max(0.001, context.deadline - monotonic())) if context else default


class TaskCancellation:
    """Task cancellation also observes shutdown/disconnect of its parent workflow."""


    def __init__(self, parent):
        self.parent, self.local = parent, Event()


    def set(self):
        self.local.set()


    def is_set(self):
        return self.local.is_set() or self.parent.is_set()


    def wait(self, timeout=None):
        deadline = monotonic() + timeout if timeout is not None else float("inf")
        while not self.is_set():
            remaining = deadline - monotonic()
            if remaining <= 0:
                return False
            self.local.wait(min(0.02, remaining))
        return True
