"""Bounded evidence discovery shared by specialist workflows."""

from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
import logging

from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.orchestration.runtime import check_active
from app.services.retrieval.service import retrieve_context

logger = logging.getLogger(__name__)


def discover_evidence(queries: list[str], document_ids: list[str], *, scope=None,
                      question="", objection="", max_searches=4) -> tuple[list, list]:
    scoped_id = (scope or {}).get("documentId")
    documents = [value for value in dict.fromkeys(document_ids) if not scoped_id or value == scoped_id]
    jobs = [(query, document_id) for query in queries[:2] for document_id in documents][:max_searches]
    results, issues = [], []


    def retrieve(query, document_id):
        check_active()
        text = f"Disputed claim: {query}\nOriginal question: {question}\nObjection: {objection}"
        return retrieve_context(text, document_id=document_id, scope=scope)

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="evidence-discovery") as pool:
        futures = [pool.submit(copy_context().run, retrieve, *job) for job in jobs]
        for future in futures:
            check_active()
            try:
                results.extend(future.result())
            except (TaskCancelled, TaskDeadline):
                raise
            except Exception as error:
                logger.warning("Evidence discovery unavailable (%s)", type(error).__name__)
                issues.append("An additional evidence search was unavailable.")
    if len(jobs) < len(queries) * len(documents):
        issues.append("Additional retrieval reached its four-search limit; some claims or PDFs were not searched again.")
    return results, issues
