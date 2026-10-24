from functools import lru_cache
from typing import Any, Mapping, Sequence
from math import isfinite

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.services.retrieval.structure_evidence import structure_description


@lru_cache(maxsize=2)
def get_reranker(model_name: str | None = None) -> CrossEncoder:
    """Load a cross-encoder once and reuse it for subsequent queries."""
    return CrossEncoder(model_name or settings.RERANKER_MODEL)


def _candidate_text(candidate: Mapping[str, Any]) -> str:
    metadata = candidate.get("metadata")
    if isinstance(metadata, Mapping):
        text = metadata.get("text")
        if isinstance(text, str):
            return text.strip()

    text = candidate.get("text")
    return text.strip() if isinstance(text, str) else ""


def rerank_chunks(
    query: str,
    candidates: Sequence[Mapping[str, Any]],
    top_k: int | None = None,
    model_name: str | None = None,
) -> list[dict[str, Any]]:

   
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty")
    if top_k is not None and top_k < 1:
        raise ValueError("top_k must be greater than zero")

    valid_candidates = [
        candidate for candidate in candidates if _candidate_text(candidate)
    ]
    if not valid_candidates:
        return []

    pairs = [(normalized_query, _ranker_text(candidate)) for candidate in valid_candidates]
    scores = list(get_reranker(model_name).predict(pairs))
    if len(scores) != len(valid_candidates) or any(not isfinite(float(score)) for score in scores):
        raise ValueError("The reranker must return one finite score for every candidate.")
    ranked = sorted(
        zip(valid_candidates, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    limit = top_k if top_k is not None else len(ranked)
    results: list[dict[str, Any]] = []
    for candidate, score in ranked[:limit]:
        result = dict(candidate)
        result["rerank_score"] = float(score)
        results.append(result)
    return results


def _ranker_text(candidate) -> str:
    metadata = candidate.get("metadata") or {}
    path = " > ".join(metadata.get("topic_path", []))
    hints = "\n".join(part for part in (f"Topic: {path}" if path else "",
                                     structure_description(metadata)) if part)
    return f"{hints}\n{_candidate_text(candidate)}" if hints else _candidate_text(candidate)
