"""Report actual source pages, including pages without selectable text."""


def source_coverage(chunks: list[dict]) -> dict:
    text_pages, empty_pages = set(), set()
    for chunk in chunks:
        start = chunk.get("page_start", chunk.get("page"))
        end = chunk.get("page_end", start)
        if not isinstance(start, int) or not isinstance(end, int) or not 1 <= start <= end:
            continue
        target = text_pages if str(chunk.get("text", "")).strip() else empty_pages
        target.update(range(start, end + 1))
    return {"read_pages": sorted(text_pages), "pages_without_text": sorted(empty_pages - text_pages)}


def coverage_note(coverage: dict) -> str:
    read = coverage.get("read_pages", [])
    empty = coverage.get("pages_without_text", [])
    if not read:
        return ""
    text = f"\nRead {len(read)} PDF pages with selectable text.\n"
    if coverage.get("strategy") == "all_page_excerpts":
        text += "\nOverview synthesized from informative excerpts selected after scanning every text page.\n"
    if empty:
        location = ", ".join(map(str, empty[:10])) + (", …" if len(empty) > 10 else "")
        text += (f"\nPDF pages without selectable text: {location} ({len(empty)} total). "
                 "Their image content was not summarized; scanned pages need OCR.\n")
    return text
