from dataclasses import dataclass
from queue import Empty, Full
from time import monotonic

from app.orchestration.runtime import check_active


@dataclass(frozen=True)
class TaskEvent:
    task_id: str
    kind: str
    data: object


def publish(queue, event):
    while True:
        check_active()
        try:
            queue.put(event, timeout=0.02)
            return
        except Full:
            continue


def drain(queue, state):
    while True:
        try:
            event = queue.get_nowait()
        except Empty:
            return
        task = state.tasks[event.task_id]
        if task.status != "running":
            continue
        if event.kind == "attempt":
            task.attempts = event.data
        elif event.kind == "text":
            if state.cancel.is_set() or task.deadline is not None and monotonic() >= task.deadline:
                continue
            task.text += event.data
        yield event


def render_event(event):
    if event.kind == "text":
        return event.data
    if event.kind == "task_finished" and event.data.error:
        return f"\n\n{event.data.error}\n"
    return None

