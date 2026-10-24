from app.services.retrieval.discovery import discover_evidence
from app.services.verification.evidence import sources_from_chunks


def targeted_search(target, claims, knowledge_base_id: str) -> tuple[list, list]:
    chunks, issues = discover_evidence([claim.text for claim in claims], target.document_ids,
        scope=target.scope, question=target.question, objection=target.objection)
    sources, invalid = sources_from_chunks(chunks, target, knowledge_base_id)
    return sources, issues + invalid
