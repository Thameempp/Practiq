from time import monotonic


def complete(future, spec, state):
    task = state.tasks[spec.task_id]
    try:
        outcome = future.result()
        task.status, task.result, task.error = outcome.status, outcome.result, outcome.error
        task.attempts, task.evidence = outcome.attempts, outcome.evidence
    except Exception:
        task.status, task.error = "failed", f"{spec.label} could not be completed. Please try again."
    task.finished_at = monotonic()


def stop_task(future, record, state, *, cancelled=False):
    spec, _, cancel = record
    cancel.set()
    future.cancel()
    task = state.tasks[spec.task_id]
    task.status = "cancelled" if cancelled else "timed_out"
    task.error = f"{spec.label} was cancelled." if cancelled else f"{spec.label} timed out. Please try again."
    task.finished_at = monotonic()


def stop_pending(pending, state, *, cancelled=False):
    for spec in pending:
        task = state.tasks[spec.task_id]
        task.status = "cancelled" if cancelled else "timed_out"
        task.error = f"{spec.label} was cancelled." if cancelled else f"{spec.label} timed out before it could start."
        task.finished_at = monotonic()
    pending.clear()
