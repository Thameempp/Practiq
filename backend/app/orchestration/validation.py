import math


def validate_plan(plan):
    ids = [task.task_id for task in plan.tasks]
    if not ids or len(ids) != len(set(ids)) or not all(ids):
        raise ValueError("A workflow requires unique, nonempty task IDs.")
    if plan.max_concurrency < 1 or not math.isfinite(plan.timeout_seconds) or plan.timeout_seconds <= 0:
        raise ValueError("Workflow concurrency and timeout must be positive.")
    for task in plan.tasks:
        if not callable(task.run) or task.retries < 0 or task.timeout_seconds <= 0 or not math.isfinite(task.timeout_seconds):
            raise ValueError("Task handlers, retries and timeouts are invalid.")
        if set(task.depends_on) - set(ids):
            raise ValueError("A task refers to an unknown dependency.")
    resolved = set()
    while len(resolved) < len(ids):
        ready = {task.task_id for task in plan.tasks if set(task.depends_on) <= resolved}
        if not ready - resolved:
            raise ValueError("Workflow dependencies contain a cycle.")
        resolved.update(ready)
