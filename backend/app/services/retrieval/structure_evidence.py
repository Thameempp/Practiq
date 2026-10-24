"""Bound map-discovered evidence and keep structural annotations out of quotes."""

from app.services.retrieval.candidates import clean_candidates
from app.services.retrieval.models import RetrievalConfig
from app.services.topics.context import TopicContext


def supplement_candidates(candidates: list[dict], context: TopicContext | None,
                          document_id: str, config: RetrievalConfig) -> list[dict]:
    discover = getattr(context, "seed_candidates", None)
    if discover is None:
        return candidates
    limit = min(8, config.max_candidates)
    seeds = clean_candidates(discover(limit), document_id)[:limit]
    by_id = {chunk["id"]: chunk for chunk in candidates}
    extra = []
    for rank, seed in enumerate(seeds, 1):
        candidate = by_id.get(seed["id"], seed)
        candidate = {**candidate, "retrieval": {**candidate.get("retrieval", {}), "structure_rank": rank}}
        extra.append(candidate)
    ids = {chunk["id"] for chunk in extra}
    primary = [chunk for chunk in candidates if chunk["id"] not in ids]
    return [*primary[:max(0, config.max_candidates - len(extra))], *extra]


def structure_description(metadata: dict) -> str:
    structure = metadata.get("document_structure")
    if not structure:
        return ""
    parts = []
    if structure.get("section_type"):
        parts.append(f"{structure['section_type']} ({structure['status']}, rule-based confidence {structure['confidence']})")
    if structure.get("printed_page"):
        parts.append(f"printed page {str(structure['printed_page'])[:30]}")
    if structure.get("page_quality") != "readable":
        parts.append(f"page quality: {structure.get('page_quality', 'unknown')}")
    if structure.get("needs_ocr"):
        parts.append("OCR required; embedded text may be incomplete")
    return "; ".join(parts)
