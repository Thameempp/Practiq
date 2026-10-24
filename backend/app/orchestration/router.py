"""Build plans only for implemented workflows; never guess a fallback handler."""

from app.orchestration.cross_document import answer_across_documents
from app.orchestration.mcq_workflow import generate_quiz_task
from app.orchestration.qa_workflow import answer_question
from app.orchestration.summary_workflow import consolidate, summarize_pdf
from app.orchestration.tasks import ExecutionPlan, TaskSpec
from app.orchestration.verification_workflow import verify_answer
from app.orchestration.structure_workflow import answer_structure
from app.services.summary.budget import summary_timeout

STREAMING_ACTIONS = frozenset({"summary", "document_qa", "cross_document_qa", "verify_answer", "document_structure"})
MESSAGE_ACTIONS = frozenset({"clarification_required", "not_found", "processing", "no_documents", "unsupported_task"})


def build_plan(decision, *, count=5, exclude_questions=()):
    if decision.action in MESSAGE_ACTIONS:
        return None
    if decision.action not in STREAMING_ACTIONS | {"mcq"}:
        raise ValueError(f"Unsupported workflow: {decision.action}")
    if not decision.documents or any(doc.status != "ready" for doc in decision.documents):
        raise ValueError("Executable workflows require ready documents.")
    if decision.action in ("document_qa", "mcq") and len(decision.documents) != 1:
        raise ValueError("This workflow requires exactly one document.")
    if decision.action == "summary":
        from app.services.generator import client
        tasks = [TaskSpec(f"summary:{doc.document_id}",
                          lambda context, document=doc: summarize_pdf(decision, document, client, context),
                          label=f"Summary of {doc.filename}", timeout_seconds=summary_timeout(doc))
                 for doc in decision.documents]
        if decision.analysis.consolidated and len(tasks) > 1:
            ids = tuple(task.task_id for task in tasks)
            tasks.append(TaskSpec("consolidate", lambda context: consolidate(context, ids, client),
                                  label="Combined summary", depends_on=ids, timeout_seconds=180))
        # Sequential per-PDF generation preserves the existing rate-limit policy.
        return ExecutionPlan(tuple(tasks), max_concurrency=1, timeout_seconds=sum(task.timeout_seconds for task in tasks))
    if decision.action == "mcq":
        handler = lambda context: generate_quiz_task(decision, context, count, exclude_questions)
    elif decision.action == "verify_answer":
        handler = lambda context: verify_answer(decision)
    elif decision.action == "document_structure":
        handler = lambda context: answer_structure(decision)
    else:
        handler = lambda context: answer_across_documents(decision) if decision.action == "cross_document_qa" else answer_question(decision)
    return ExecutionPlan((TaskSpec(decision.action, handler, label=decision.action.replace("_", " ").capitalize()),))
