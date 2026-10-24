from collections.abc import Iterator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

from app.orchestration.errors import TaskCancelled, TaskDeadline, TaskFailure
from app.orchestration.runtime import TaskContext, current_task


@dataclass
class TaskOutcome:
    status: str
    attempts: int
    evidence: list
    result: object = None
    error: str | None = None


def run_task(spec, deadline, cancel, outputs, send):
    context = TaskContext(deadline, cancel, outputs, send)
    token = current_task.set(context)
    attempt = 0
    try:
        for attempt in range(1, spec.retries + 2):
            context.check()
            send("attempt", attempt)
            try:
                value = spec.run(context)
                result = _consume(value, context) if isinstance(value, Iterator) else value
                context.check()
                return TaskOutcome("succeeded", attempt, context.evidence, result)
            except (TaskCancelled, TaskDeadline):
                raise
            except Exception as error:
                status = getattr(error, "status_code", None)
                transient = isinstance(error, (ConnectionError, TimeoutError)) or status in (408, 429) or isinstance(status, int) and status >= 500
                if attempt > spec.retries or context.published or not transient:
                    raise
                context.cancel.wait(min(0.1 * 2 ** (attempt - 1), 1.0))
    except TaskCancelled:
        return TaskOutcome("cancelled", attempt, context.evidence, error=f"{spec.label} was cancelled.")
    except TaskDeadline:
        return TaskOutcome("timed_out", attempt, context.evidence, error=f"{spec.label} timed out. Please try again.")
    except Exception as error:
        logger.warning("Workflow task %s failed (%s)", spec.task_id, type(error).__name__)
        message = str(error) if isinstance(error, TaskFailure) else f"{spec.label} could not be completed. Please try again."
        return TaskOutcome("failed", attempt, context.evidence, error=message)
    finally:
        current_task.reset(token)


def _consume(iterator, context):
    parts = []
    try:
        while True:
            context.check()
            try:
                text = next(iterator)
            except StopIteration as done:
                return done.value if done.value is not None else "".join(parts)
            if not isinstance(text, str):
                raise TypeError("Streaming task output must be text.")
            context.emit(text)
            parts.append(str(text))
    finally:
        close = getattr(iterator, "close", None)
        if close:
            close()
