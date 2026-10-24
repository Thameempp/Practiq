from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class HierarchyScope:
    title: str
    node_id: str = ""
    node_type: str = ""
    document_id: str = ""
    filename: str = ""
    page: int | None = None
    page_label: str = ""
    summary: str = ""
    excerpt: str = ""
    descendant_titles: tuple[str, ...] = field(default_factory=tuple)


def parse_scope(raw_scope: Mapping[str, Any] | str | None) -> HierarchyScope | None:
    """Normalize frontend selected hierarchy node payloads."""
    if raw_scope is None:
        return None

    if isinstance(raw_scope, HierarchyScope):
        return raw_scope

    if isinstance(raw_scope, str):
        title = raw_scope.strip()
        return HierarchyScope(title=title) if title else None

    title = str(raw_scope.get("title") or "").strip()
    if not title:
        return None

    descendant_titles = tuple(
        str(title).strip()
        for title in raw_scope.get("descendantTitles", [])
        if str(title).strip()
    )

    return HierarchyScope(
        title=title,
        node_id=str(raw_scope.get("id") or "").strip(),
        node_type=str(raw_scope.get("type") or "").strip(),
        document_id=str(raw_scope.get("documentId") or "").strip(),
        filename=str(raw_scope.get("filename") or "").strip(),
        page=_coerce_page(raw_scope.get("page")),
        page_label=str(raw_scope.get("pageLabel") or "").strip(),
        summary=str(raw_scope.get("summary") or "").strip(),
        excerpt=str(raw_scope.get("excerpt") or "").strip(),
        descendant_titles=descendant_titles,
    )


def build_scope_search_text(scope: HierarchyScope | None) -> str:
    """Compact text that biases retrieval toward the selected tree node."""
    if scope is None:
        return ""

    parts = [scope.title]

    if scope.node_type:
        parts.append(scope.node_type)
    if scope.filename:
        parts.append(scope.filename)
    if scope.page_label:
        parts.append(scope.page_label)
    if scope.summary:
        parts.append(scope.summary)
    if scope.descendant_titles:
        parts.append(" ".join(scope.descendant_titles[:20]))
    if scope.excerpt:
        parts.append(scope.excerpt[:700])

    return " ".join(part for part in parts if part).strip()


def build_scope_prompt(scope: HierarchyScope | None) -> str:
    """Human-readable focus metadata for the LLM prompt.

    Do not include node excerpts here. Document text must reach the LLM only
    through ranked retrieval chunks.
    """
    if scope is None:
        return ""

    lines = [f"Selected hierarchy node: {scope.title}"]

    if scope.node_type:
        lines.append(f"Node type: {scope.node_type}")
    if scope.filename:
        lines.append(f"Document: {scope.filename}")
    if scope.page_label:
        lines.append(f"Location: {scope.page_label}")
    if scope.descendant_titles:
        child_titles = ", ".join(scope.descendant_titles[:20])
        lines.append(f"Child topics: {child_titles}")
    if scope.summary:
        lines.append(f"Node summary: {scope.summary}")

    return "\n".join(lines)


def _coerce_page(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
