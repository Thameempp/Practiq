from collections.abc import Mapping

from app.services.embedding import get_embedding
from app.services.pinecone_index import get_index


def search_vector(query_text: str, top_k: int = 10, document_id: str | None = None, *, topic_context=None) -> list[dict]:
    query = query_text.strip()
    if not query:
        raise ValueError("query_text must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be greater than zero")
    kwargs = {"vector": get_embedding(query), "top_k": top_k, "include_metadata": True}
    if document_id:
        kwargs["filter"] = {"document_id": {"$eq": document_id}}
        if topic_context and (restriction := topic_context.vector_filter()):
            clauses = restriction.get("$and", [restriction])
            kwargs["filter"] = {"$and": [kwargs["filter"], *clauses]}
    response = get_index().query(**kwargs)
    matches = _field(response, "matches", [])
    results = []
    for match in matches:
        metadata = _field(match, "metadata", {})
        text = metadata.get("text") if isinstance(metadata, Mapping) else None
        if isinstance(text, str) and text.strip():
            results.append({"id": _field(match, "id"), "score": float(_field(match, "score", 0) or 0),
                            "metadata": dict(metadata)})
    return results


def _field(value, name, default=None):
    return value.get(name, default) if isinstance(value, Mapping) else getattr(value, name, default)
