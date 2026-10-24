from collections.abc import Iterator

from app.citations.catalog import emit_metadata
from app.citations.store import save_sources, source_for
from app.orchestration.agent_activity import agent_activity
from app.orchestration.decision import RoutingDecision
from app.orchestration.runtime import capture_evidence, check_active
from app.services.understanding.answers import structure_answer
from app.services.understanding.query import structure_query
from app.services.understanding.service import document_map


def answer_structure(decision: RoutingDecision) -> Iterator[str]:
    query = structure_query(decision.question)
    if query is None:
        raise ValueError("A structural document question is required.")
    labels = {}
    for document in decision.documents:
        check_active()
        with agent_activity("Document Understanding"):
            mapped = document_map(document.document_id, document.knowledge_base_id)


            def link(start: int, end: int) -> str:
                source = source_for(document, start, "", page_end=end)
                label = labels.setdefault(source.id, str(len(labels) + 1))
                save_sources([source])
                capture_evidence([{"source": source, "page_start": start, "page_end": end,
                                   "metadata": {"document_id": document.document_id}}])
                emit_metadata("sources", [source.public()])
                emit_metadata("citation", {"id": source.id, "label": label})
                return f"[{label}](#source-{source.id})"

            yield structure_answer(mapped, query, link) + "\n\n"
