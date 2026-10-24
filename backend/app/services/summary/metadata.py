"""Bound hints independently so long early outlines cannot erase the user focus."""


def summary_metadata(outline, request: str, *, include_outline: bool) -> str:
    focus = request.encode()[:1000].decode("utf-8", errors="ignore")
    titles = [str(title).strip() for title in (outline or []) if str(title).strip()]
    if not include_outline:
        titles = []
    if len(titles) > 12:
        titles = [titles[round(index * (len(titles) - 1) / 11)] for index in range(12)]
    limit = min(100, 900 // max(1, len(titles)) - 1)
    hints = "\n".join(title.encode()[:limit].decode("utf-8", errors="ignore") for title in titles)
    return (f"User focus:\n{focus}\nOutline hints sampled across the document "
            f"(structure only, never factual evidence):\n{hints}")
