"""Scan every source page and reduce large books locally before any model call."""

from collections import Counter
from hashlib import sha256
from math import log

from app.orchestration.runtime import check_active
from app.services.retrieval.lexical import terms
from app.services.summary.coverage import source_coverage
from app.services.summary.extractive import page_digest


def prepare_source(chunks: list[dict], config) -> tuple[list[dict], dict, str]:
    coverage, grouped, digest = source_coverage(chunks), {}, sha256()
    for chunk in chunks:
        check_active()
        text = chunk.get("text", "")
        if not isinstance(text, str):
            return chunks, coverage, ""
        start = chunk.get("page_start", chunk.get("page"))
        end = chunk.get("page_end", start)
        digest.update(f"{start}:{end}:{len(text)}:".encode())
        digest.update(text.encode())
        grouped.setdefault((start, end), []).append(text)
    original_chars = sum(len(chunk.get("text", "")) for chunk in chunks)
    pages = [{"page": start, "page_start": start, "page_end": end, "text": "\n".join(texts)}
             for (start, end), texts in grouped.items()]
    compact = len(coverage["read_pages"]) >= config.digest_threshold_pages
    if compact:
        frequencies = Counter(word for page in pages for word in set(terms(page["text"])))
        idf = {word: 1 + log((len(pages) + 1) / (count + 1)) for word, count in frequencies.items()}
        for page in pages:
            check_active()
            page["text"] = page_digest(page["text"], idf, config.page_digest_chars)
    coverage.update(strategy="all_page_excerpts" if compact else "full_text",
                    source_characters=original_chars,
                    mapped_characters=sum(len(page["text"]) for page in pages))
    return pages, coverage, digest.hexdigest()
