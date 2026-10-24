from dataclasses import dataclass

from app.services.context import normalize_question
from app.services.hierarchy import parse_scope
from app.services.hierarchy.scope import HierarchyScope


@dataclass(frozen=True)
class RetrievalQuery:
    question: str
    document_id: str
    search_text: str
    scope: HierarchyScope | None = None


def prepare_query(question: str, scope=None, document_id=None) -> RetrievalQuery:
    normalized, legacy_scope = normalize_question(question)
    parsed = parse_scope(scope) or parse_scope(legacy_scope)
    explicit = (document_id or "").strip()
    scoped = parsed.document_id.strip() if parsed else ""
    if explicit and scoped and explicit != scoped:
        raise ValueError("The selected section belongs to a different document.")
    document = explicit or scoped
    if not normalized or not document:
        raise ValueError("A question and uploaded document are required.")
    titles = [parsed.title, *parsed.descendant_titles[:10]] if parsed else []
    focus = " ".join(titles)[:1000]
    return RetrievalQuery(normalized, document, f"{normalized} {focus}".strip(), parsed)
