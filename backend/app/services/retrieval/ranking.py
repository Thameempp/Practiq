"""Only accept finite reranker scores for candidates actually supplied to it."""

from app.services.retrieval.candidates import finite_score


def rank_candidates(pairs, candidates, *, limit, minimum=None):
    by_id = {chunk["id"]: chunk for chunk in candidates}
    ranked = {}
    for chunk, raw_score in pairs:
        chunk_id = chunk.get("id")
        score = finite_score(raw_score)
        if chunk_id not in by_id or score is None or minimum is not None and score < minimum:
            continue
        if chunk_id not in ranked or score > ranked[chunk_id]["rerank_score"]:
            ranked[chunk_id] = {**by_id[chunk_id], "rerank_score": score}
    return sorted(ranked.values(), key=lambda chunk: chunk["rerank_score"], reverse=True)[:limit]


def reciprocal_rank_fusion(dense, sparse, *, k=60):
    fused = {}
    for method, chunks in (("dense", dense), ("bm25", sparse)):
        seen = set()
        for rank, chunk in enumerate(chunks, start=1):
            chunk_id = chunk["id"]
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            if chunk_id not in fused:
                fused[chunk_id] = {**chunk, "rrf_score": 0.0, "retrieval": {}}
            result = fused[chunk_id]
            result["rrf_score"] += 1.0 / (k + rank)
            result["retrieval"][f"{method}_rank"] = rank
            result["retrieval"][f"{method}_score"] = chunk["score"]
    return sorted(fused.values(), key=lambda chunk: chunk["rrf_score"], reverse=True)
