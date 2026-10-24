from collections import Counter
from dataclasses import dataclass

from app.services.hierarchy.patterns import (
    RE_ANSWER_CHOICE,
    RE_BULLET_PREFIX,
    RE_LEADING_LIST_NUMBER,
    RE_NO_LETTERS,
    RE_NUMBERED_PREFIX,
)


@dataclass(frozen=True)
class StyleProfile:
    body_size: float
    heading_sizes: tuple[float, ...]
    document_title_size: float | None
    left_margin: float
    indent_step: float


def build_style_profile(lines: list[dict]) -> StyleProfile:
    """Infer document-specific text size and indentation tiers."""
    readable_lines = [line for line in lines if RE_NO_LETTERS.search(line["text"])]
    if not readable_lines:
        return StyleProfile(12.0, (), None, 0.0, 24.0)

    body_size = _dominant_body_size(readable_lines)
    size_counts = Counter(line["size"] for line in readable_lines)
    heading_sizes = tuple(
        sorted(
            (size for size in size_counts if size >= body_size + 2.0),
            reverse=True,
        )
    )
    document_title_size = _document_title_size(heading_sizes, body_size)
    left_margin = min(line["x"] for line in readable_lines)

    return StyleProfile(
        body_size=body_size,
        heading_sizes=heading_sizes,
        document_title_size=document_title_size,
        left_margin=left_margin,
        indent_step=24.0,
    )


def classify_line(line: dict, profile: StyleProfile) -> int | None:
    """Classify a line as document/section/subsection/topic/subtopic."""
    text = line["text"]

    if not is_candidate_text(text):
        return None

    if _is_document_title(line, profile):
        return 1

    numbered_level = _numbered_heading_level(line, profile)
    if numbered_level is not None:
        return numbered_level

    visual_level = _visual_heading_level(line, profile)
    if visual_level is not None:
        return visual_level

    if is_list_item(text):
        return 5 if _indent_depth(line, profile) >= 2 else 4

    return None


def dominant_body_size(lines: list[dict]) -> float:
    """Compatibility helper for older callers."""
    readable_lines = [line for line in lines if RE_NO_LETTERS.search(line["text"])]
    if not readable_lines:
        return 12.0
    return _dominant_body_size(readable_lines)


def is_candidate_text(text: str) -> bool:
    if len(text) < 3 or len(text) > 140:
        return False
    if not RE_NO_LETTERS.search(text):
        return False
    if RE_ANSWER_CHOICE.match(text):
        return False
    return True


def is_list_item(text: str) -> bool:
    return bool(RE_BULLET_PREFIX.match(text) or RE_LEADING_LIST_NUMBER.match(text))


def _dominant_body_size(lines: list[dict]) -> float:
    return Counter(line["size"] for line in lines).most_common(1)[0][0]


def _document_title_size(heading_sizes: tuple[float, ...], body_size: float) -> float | None:
    if not heading_sizes:
        return None

    largest = heading_sizes[0]
    next_largest = heading_sizes[1] if len(heading_sizes) > 1 else body_size
    if largest >= next_largest + 2.5:
        return largest
    return None


def _is_document_title(line: dict, profile: StyleProfile) -> bool:
    return (
        profile.document_title_size is not None
        and line["size"] >= profile.document_title_size - 0.2
    )


def _numbered_heading_level(line: dict, profile: StyleProfile) -> int | None:
    match = RE_NUMBERED_PREFIX.match(line["text"])
    if not match:
        return None

    number = match.group(1)
    depth = number.count(".") + 1

    if _looks_like_ordered_body_step(line, profile, depth):
        return 4 if _indent_depth(line, profile) < 2 else 5

    return min(depth + 1, 5)


def _looks_like_ordered_body_step(line: dict, profile: StyleProfile, depth: int) -> bool:
    if depth > 1:
        return False
    if line["size"] >= _minimum_heading_size(profile):
        return False
    return True


def _visual_heading_level(line: dict, profile: StyleProfile) -> int | None:
    text = line["text"]
    size = line["size"]
    indent_depth = _indent_depth(line, profile)
    is_heading_sized = size >= _minimum_heading_size(profile)

    if text.endswith(":") and (line["bold"] or is_heading_sized):
        return min(3 + indent_depth, 5)

    if is_heading_sized and _is_short_heading_text(text):
        return min(3 + indent_depth, 5)

    if line["bold"] and size >= profile.body_size + 0.5 and _is_short_heading_text(text):
        return min(3 + indent_depth, 5)

    return None


def _minimum_heading_size(profile: StyleProfile) -> float:
    if profile.heading_sizes:
        return min(profile.heading_sizes)
    return profile.body_size + 1.0


def _indent_depth(line: dict, profile: StyleProfile) -> int:
    if profile.indent_step <= 0:
        return 0
    return max(0, round((line["x"] - profile.left_margin) / profile.indent_step))


def _is_short_heading_text(text: str) -> bool:
    if is_list_item(text):
        return False
    words = text.split()
    if len(words) > 12:
        return False
    sentence_endings = (".", "?", "!")
    return not text.endswith(sentence_endings)
