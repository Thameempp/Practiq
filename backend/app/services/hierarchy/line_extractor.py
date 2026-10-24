import pymupdf

from app.services.hierarchy.patterns import (
    RE_BULLET_MARKER,
    RE_LIST_NUMBER,
    clean_text,
    is_bold,
)


def collect_lines(doc) -> list[dict]:
    """Collect readable PDF lines with style and position metadata."""
    raw_lines: list[dict] = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                parsed = _parse_line(line, page_num)
                if parsed:
                    raw_lines.append(parsed)

    raw_lines.sort(key=lambda item: (item["page"], item["y"], item["x"]))
    return _merge_same_row_markers(raw_lines)


def _parse_line(line: dict, page_num: int) -> dict | None:
    spans = line.get("spans", [])
    if not spans:
        return None

    text = clean_text(" ".join(span.get("text", "") for span in spans))
    if not text:
        return None

    flags = 0
    for span in spans:
        flags |= span.get("flags", 0)

    bbox = line.get("bbox") or (0, 0, 0, 0)
    return {
        "text": text,
        "size": max(round(span["size"], 1) for span in spans),
        "flags": flags,
        "bold": is_bold(flags),
        "page": page_num,
        "x": float(bbox[0]),
        "y": float(bbox[1]),
    }


def _merge_same_row_markers(lines: list[dict]) -> list[dict]:
    """Merge bullet/number marker lines with their same-row text."""
    merged: list[dict] = []
    index = 0

    while index < len(lines):
        current = dict(lines[index])
        next_line = lines[index + 1] if index + 1 < len(lines) else None

        same_row = (
            next_line
            and next_line["page"] == current["page"]
            and abs(next_line["y"] - current["y"]) <= 2.0
            and next_line["x"] > current["x"]
        )

        if same_row and _is_marker(current["text"]):
            current = _merge_marker_with_text(current, next_line)
            index += 2
        else:
            index += 1

        merged.append(current)

    return merged


def _is_marker(text: str) -> bool:
    return bool(RE_BULLET_MARKER.match(text) or RE_LIST_NUMBER.match(text))


def _merge_marker_with_text(marker_line: dict, text_line: dict) -> dict:
    marker = "•"
    if not RE_BULLET_MARKER.match(marker_line["text"]):
        marker = f"{marker_line['text'].rstrip(').')}."

    merged = dict(marker_line)
    merged["text"] = clean_text(f"{marker} {text_line['text']}")
    merged["size"] = max(marker_line["size"], text_line["size"])
    merged["flags"] |= text_line["flags"]
    merged["bold"] = marker_line["bold"] or text_line["bold"]
    return merged
