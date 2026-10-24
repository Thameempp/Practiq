from time import monotonic

from app.orchestration.runtime import TaskCancellation
from app.orchestration.events import TaskEvent, publish
from app.orchestration.state import TERMINAL
from app.orchestration.worker import run_task


def launch_ready(pending, active, pool, slots, plan, state, queue, workflow_deadline):
    for spec in list(pending):
        if len(active) >= plan.max_concurrency:
            break
        task = state.tasks[spec.task_id]
        dependencies = [state.tasks[value].status for value in spec.depends_on]
        if any(status not in TERMINAL for status in dependencies):
            continue
        pending.remove(spec)
        if any(status != "succeeded" for status in dependencies):
            task.status, task.error = "skipped", f"{spec.label} was skipped because a required task did not succeed."
            task.finished_at = monotonic()
            continue
        if not slots.acquire(blocking=False):
            task.status, task.error = "failed", "The workflow service is busy. Please try again."
            task.finished_at = monotonic()
            continue
        cancel = TaskCancellation(state.cancel)
        task.status, task.started_at = "running", monotonic()
        deadline = min(workflow_deadline, task.started_at + spec.timeout_seconds)
        task.deadline = deadline
        send = lambda kind, data, task_id=spec.task_id: publish(queue, TaskEvent(task_id, kind, data))
        outputs = {key: result.result for key, result in state.tasks.items() if result.status == "succeeded"}
        try:
            future = pool.submit(run_task, spec, deadline, cancel, outputs, send)
        except RuntimeError:
            slots.release()
            task.status, task.error, task.finished_at = "failed", "The workflow service is unavailable.", monotonic()
            continue
        future.add_done_callback(lambda done: slots.release())
        active[future] = (spec, deadline, cancel)
