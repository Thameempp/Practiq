"""Bounded shared worker pool; deadlines never create replacement worker pools."""

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from queue import Queue
from threading import BoundedSemaphore
from time import monotonic

from app.orchestration.completion import complete, stop_pending, stop_task
from app.orchestration.dispatch import launch_ready
from app.orchestration.events import TaskEvent, drain
from app.orchestration.state import TaskResult
from app.orchestration.validation import validate_plan


class TaskExecutor:
    def __init__(self, max_workers=4, max_pending=8):
        if max_workers < 1 or max_pending < max_workers:
            raise ValueError("Worker and queue limits are invalid.")
        self.pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="practiq-workflow")
        self.slots = BoundedSemaphore(max_pending)
        self.runs = set()


    def events(self, plan, state):
        validate_plan(plan)
        if state.status != "pending":
            raise ValueError("A workflow can only be executed once.")
        state.tasks = {spec.task_id: TaskResult(spec.task_id) for spec in plan.tasks}
        state.status = "running"
        self.runs.add(state.cancel)
        pending, active, queue = list(plan.tasks), {}, Queue(maxsize=128)
        deadline = monotonic() + plan.timeout_seconds
        try:
            while pending or active:
                cancelled = state.cancel.is_set()
                if cancelled or monotonic() >= deadline:
                    affected = {spec.task_id for spec in pending} | {value[0].task_id for value in active.values()}
                    stop_pending(pending, state, cancelled=cancelled)
                    for future, record in list(active.items()):
                        stop_task(future, record, state, cancelled=cancelled)
                    active.clear()
                    for task in state.tasks.values():
                        if task.task_id in affected:
                            yield TaskEvent(task.task_id, "task_finished", task)
                    break
                yield from drain(queue, state)
                for future, record in list(active.items()):
                    if future.done():
                        yield from drain(queue, state)
                        complete(future, record[0], state)
                        del active[future]
                        yield TaskEvent(record[0].task_id, "task_finished", state.tasks[record[0].task_id])
                    elif monotonic() >= record[1]:
                        stop_task(future, record, state)
                        del active[future]
                        yield TaskEvent(record[0].task_id, "task_finished", state.tasks[record[0].task_id])
                previous = {key: value.status for key, value in state.tasks.items()}
                launch_ready(pending, active, self.pool, self.slots, plan, state, queue, deadline)
                for key, task in state.tasks.items():
                    if previous[key] == "pending" and task.status in ("skipped", "failed"):
                        yield TaskEvent(key, "task_finished", task)
                yield TaskEvent("", "tick", None)
                if active:
                    wait(active, timeout=0.02, return_when=FIRST_COMPLETED)
            yield from drain(queue, state)
        finally:
            if pending or active:
                state.cancel.set()
                stop_pending(pending, state, cancelled=True)
                for future, record in active.items():
                    stop_task(future, record, state, cancelled=True)
            state.finish()
            self.runs.discard(state.cancel)


    def close(self):
        for cancel in list(self.runs):
            cancel.set()
        self.pool.shutdown(wait=False, cancel_futures=True)
