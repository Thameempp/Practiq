"""Expand, select, and render evidence under one consistent context budget."""

from app.services.retrieval.candidates import clean_candidates
from app.services.retrieval.diversity import next_candidate
from app.services.retrieval.structure_evidence import structure_description


def format_chunk(chunk) -> str:
    metadata = chunk.get("metadata") or {}
    filename = metadata.get("filename") or "Uploaded PDF"
    start, end = chunk["page_start"], chunk["page_end"]
    location = f"page {start}" if start == end else f"pages {start}-{end}"
    source = chunk.get("source")
    if source:
        filename = source.filename
    marker = f"[source_id={source.id}] " if source else ""
    topic = " > ".join(metadata.get("topic_path", []))
    heading = f"\nTopic path (structure only): {topic}" if topic else ""
    structure = structure_description(metadata)
    heading += f"\nDocument map (structure only, not factual evidence): {structure}" if structure else ""
    return f"{marker}[document {filename}, PDF {location}]{heading}\n{chunk['text']}"


def format_context(chunks) -> str:
    return "\n\n".join(format_chunk(chunk) for chunk in chunks)


def select_context(chunks, count_tokens, config):
    selected, seen = [], set()
    available = config.max_context_tokens - config.reserved_tokens
    remaining = list(chunks)
    while remaining:
        chunk = next_candidate(remaining, selected, config.diversity_weight)
        remaining.remove(chunk)
        key = ((chunk.get("metadata") or {}).get("document_id"), " ".join(chunk["text"].split()).casefold())
        if key in seen:
            continue
        candidate = [*selected, chunk]
        if count_tokens(format_context(candidate)) > available:
            continue
        selected.append(chunk)
        seen.add(key)
        if len(selected) >= config.final_top_k:
            break
    return selected


def expand_candidates(candidates, fetch_neighbors, document_id, config, topic_context=None):
    primary = candidates[:config.max_candidates]
    if fetch_neighbors is None or config.neighbor_window == 0:
        return primary
    neighbors = fetch_neighbors(primary, document_id=document_id, window=config.neighbor_window)
    if topic_context:
        neighbors = topic_context.apply(neighbors)
    by_id = {chunk["id"]: chunk for chunk in primary}
    for chunk in clean_candidates(neighbors, document_id):
        if len(by_id) >= config.max_candidates:
            break
        if chunk["id"] not in by_id:
            by_id[chunk["id"]] = {**chunk, "retrieval": {"neighbor": True}}
    return list(by_id.values())
