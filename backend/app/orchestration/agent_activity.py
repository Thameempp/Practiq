"""Request-local agent lifetimes, published separately from response text."""

from contextlib import contextmanager
from uuid import uuid4

from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.orchestration.runtime import current_task

AGENT_NAMES = {
    "DocumentUnderstandingAgent": "Document Understanding",
    "RetrievalAgent": "Retrieval",
    "PDFSummaryAgent": "PDF Summary",
    "MCQGenerationAgent": "MCQ Generation",
    "EvaluationAgent": "Evaluation",
    "AnswerVerifierAgent": "Answer Verifier",
}


@contextmanager
def agent_activity(name: str):
    context = current_task.get()
    if context is None:
        yield
        return
    activity = {"id": uuid4().hex, "name": AGENT_NAMES.get(name, name)}
    context.send("agent", {**activity, "state": "started"})
    try:
        yield
    finally:
        try:
            context.check()
            context.send("agent", {**activity, "state": "finished"})
        except (TaskCancelled, TaskDeadline):
            pass  # The stream closes and clears remaining activity on cancellation.
