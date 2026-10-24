"""Prefer novel evidence among close reranker scores; spread exact lexical ties."""

from itertools import groupby
from math import exp

from app.services.retrieval.lexical import terms


def next_candidate(chunks: list[dict], selected: list[dict], weight: float) -> dict:
    if not selected or not weight or any("rerank_score" not in chunk for chunk in chunks):
        return chunks[0]
    maximum = max(chunk["rerank_score"] for chunk in chunks)
    used = [set(terms(chunk["text"])) for chunk in selected]
    pages = {(chunk["metadata"].get("document_id"), chunk["page_start"]) for chunk in selected}


    def score(chunk):
        tokens = set(terms(chunk["text"]))
        overlap = max((len(tokens & prior) / max(1, len(tokens | prior)) for prior in used), default=0)
        relevance = exp(chunk["rerank_score"] - maximum)
        new_page = (chunk["metadata"].get("document_id"), chunk["page_start"]) not in pages
        return (1 - weight) * relevance - weight * overlap, new_page

    return max(chunks, key=score)


def lexical_top(chunks: list[dict], limit: int) -> list[dict]:
    selected = []
    for _, group in groupby(sorted(chunks, key=lambda chunk: chunk["score"], reverse=True),
                            key=lambda chunk: chunk["score"]):
        pages = {}
        for chunk in group:
            pages.setdefault(chunk["page_start"], []).append(chunk)
        while pages and len(selected) < limit:
            keys = sorted(pages)
            count = min(len(keys), limit - len(selected))
            indices = [len(keys) // 2] if count == 1 else [round(i * (len(keys) - 1) / (count - 1)) for i in range(count)]
            for index in indices:
                page = keys[index]
                selected.append(pages[page].pop(0))
                if not pages[page]:
                    del pages[page]
        if len(selected) == limit:
            break
    return selected
