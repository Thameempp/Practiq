"""Rank excerpts from the entire page; never assume its opening is representative."""

from collections import Counter
from math import log1p, sqrt
import re
from textwrap import wrap

from app.services.retrieval.lexical import terms


def page_digest(text: str, idf: dict[str, float], limit: int) -> str:
    if len(text) <= limit:
        return text
    counts = Counter(terms(text))
    passages = list(dict.fromkeys(piece for paragraph in re.split(r"(?<=[.!?。！？])\s+|\n+", text)
                                 for piece in wrap(paragraph, width=min(300, limit),
                                     break_long_words=False, break_on_hyphens=False) if piece))
    ranked = []
    for index, passage in enumerate(passages):
        words = set(terms(passage))
        score = sum((1 + log1p(counts[word])) * idf.get(word, 1) for word in words) / sqrt(max(1, len(words)))
        if re.search(r"\b(defined|means|principle|result|conclusion|therefore|however|limitation)\b|[=∑∫]", passage, re.I):
            score *= 1.5
        ranked.append((index, passage, words, score))
    selected, seen, size = [], set(), 0
    while ranked:
        ranked = [item for item in ranked if size + len(item[1]) + bool(selected) <= limit]
        if not ranked:
            break
        item = max(ranked, key=lambda item: item[3] / (1 + len(item[2] & seen)))
        ranked.remove(item)
        selected.append(item)
        seen.update(item[2])
        size += len(item[1]) + (len(selected) > 1)
    # An atomic expression longer than the budget stays intact for normal splitting.
    return "\n".join(item[1] for item in sorted(selected)) if selected else text
