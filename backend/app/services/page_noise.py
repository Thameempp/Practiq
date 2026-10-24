import re
from collections import Counter
from collections.abc import Iterable
from math import ceil
from typing import Any

MIN_PAGES = 3
MIN_PAGE_RATIO = 0.3
MIN_FUSED_KEY_CHARS = 8

_DIGITS = re.compile(r"\d+")
_HAS_LETTER = re.compile(r"[^\W\d_]")


def line_key(text: str) -> str:
    """Normalise a line so running headers match across pages (case, spacing, numbers)."""
    return _DIGITS.sub("#", " ".join(text.lower().split()))


def find_repeated_keys(page_lines: list[Iterable[str]]) -> set[str]:
    """Keys of text lines that recur on many pages: headers, footers, watermarks, URLs."""
    threshold = max(MIN_PAGES, ceil(len(page_lines) * MIN_PAGE_RATIO))
    counts: Counter[str] = Counter()

    for lines in page_lines:
        counts.update({
            key for key in map(line_key, lines) if _HAS_LETTER.search(key)
        })

    return {key for key, count in counts.items() if count >= threshold}


def strip_repeated_lines(lines: Iterable[str], keys: set[str]) -> list[str]:
    """Drop repeated lines, and cut the same text out of lines it is fused into."""
    fused = _fused_pattern(keys)
    kept = (line for line in lines if line_key(line) not in keys)
    return [fused.sub(" ", line) if fused else line for line in kept]


def clean_pages(pages: list[dict]) -> list[dict]:
    repeated = find_repeated_keys([page["text"].splitlines() for page in pages])
    return [{**page, "text": "\n".join(strip_repeated_lines(page["text"].splitlines(), repeated))}
            for page in pages]


def drop_repeated_lines(lines: list[dict[str, Any]], page_count: int) -> list[dict[str, Any]]:
    """Filter positioned lines ({"text", "page"}) whose text repeats across pages."""
    by_page: list[list[str]] = [[] for _ in range(page_count)]
    for line in lines:
        by_page[line["page"] - 1].append(line["text"])

    keys = find_repeated_keys(by_page)
    if not keys:
        return lines

    fused = _fused_pattern(keys)
    return [
        {**line, "text": fused.sub(" ", line["text"]).strip()} if fused else line
        for line in lines
        if line_key(line["text"]) not in keys
    ]


def _fused_pattern(keys: set[str]) -> re.Pattern[str] | None:
    """Long, digit-free keys (URLs, watermarks) are safe to remove from inside other lines."""
    literals = [
        re.escape(key) for key in keys
        if "#" not in key and len(key) >= MIN_FUSED_KEY_CHARS
    ]
    return re.compile("|".join(literals), re.IGNORECASE) if literals else None
