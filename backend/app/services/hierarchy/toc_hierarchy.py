from collections.abc import Callable

from app.services.hierarchy.patterns import clean_text
from app.services.page_noise import find_repeated_keys, strip_repeated_lines

MIN_TOC_ENTRIES = 5
EXCERPT_CHARS = 400

_NODE_TYPES = {1: "section", 2: "subsection", 3: "topic"}
_FRONT_MATTER_TITLES = {
    "cover", "front cover", "back cover", "half-title", "half title", "title",
    "title page", "copyright", "copyright page", "dedication", "colophon",
    "imprint", "about the publisher", "blank page", "licence", "license",
}


def hierarchy_from_toc(
    toc: list[list],
    excerpt_for: Callable[[int, str], str],
) -> list[dict]:
    """Nest a PDF outline ([level, title, page] entries) into frontend hierarchy nodes."""
    roots: list[dict] = []
    stack: list[tuple[int, dict]] = []

    for position, (level, title, page) in enumerate(toc, start=1):
        title = clean_text(str(title))
        if not title or page < 1 or title.lower() in _FRONT_MATTER_TITLES:
            continue

        node_type = _NODE_TYPES.get(level, "subtopic")
        node = {
            "id": f"{node_type}-{position}",
            "title": title,
            "type": node_type,
            "page": page,
            "pageLabel": f"p. {page}",
            "summary": "",
            "excerpt": excerpt_for(page, title),
            "children": [],
        }

        while stack and stack[-1][0] >= level:
            stack.pop()
        (stack[-1][1]["children"] if stack else roots).append(node)
        stack.append((level, node))

    return roots


def toc_hierarchy_for(doc) -> list[dict]:
    """Hierarchy from the PDF's own bookmarks, or [] when it has too few to trust."""
    toc = doc.get_toc()
    if len(toc) < MIN_TOC_ENTRIES:
        return []

    page_lines = [page.get_text("text").splitlines() for page in doc]
    repeated = find_repeated_keys(page_lines)
    page_text: dict[int, str] = {}


    def excerpt_for(page: int, title: str) -> str:
        if page not in page_text:
            lines = strip_repeated_lines(page_lines[page - 1], repeated) if page <= len(doc) else []
            page_text[page] = clean_text(" ".join(lines))
        text = page_text[page]
        start = text.lower().find(title.lower())
        if start != -1:
            text = text[start + len(title):]
        return text.strip()[:EXCERPT_CHARS]

    return hierarchy_from_toc(toc, excerpt_for)
