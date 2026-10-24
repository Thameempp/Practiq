"""Retrieval owns canonical topic selection and evidence-scope checks."""

import re

from app.services.hierarchy import parse_scope
from app.services.pdf_source import registered_document
from app.services.retrieval.lexical import terms
from app.services.topics.anchors import token
from app.services.topics.context import TopicContext
from app.services.topics.storage import load_topics


def resolve_topics(document_id: str, scope=None, question: str = "") -> TopicContext | None:
    parsed = parse_scope(scope)
    if parsed and parsed.document_id and parsed.document_id != document_id:
        raise ValueError("The selected topic belongs to a different PDF.")
    loaded = load_topics(document_id)
    if loaded is None:
        if parsed and registered_document(document_id) is not None:
            raise ValueError("This PDF has no reliable topic index. Upload the original PDF again to select topics.")
        return None
    index, words = loaded
    selected = None
    if parsed:
        matches = [node for node in index["nodes"] if (node["id"] == parsed.node_id if parsed.node_id
                   else token(node["title"]) == token(parsed.title))]
        if len(matches) != 1 or not matches[0]["reliable"]:
            raise ValueError("The topic is missing, ambiguous, or has uncertain boundaries. Select a valid outline node.")
        selected = matches[0]
    query = set(terms(question))


    def matches_query(node):
        title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", node["title"])
        words = set(terms(title))
        return bool(words) and words.issubset(query)
    preferred = tuple(sorted((node for node in index["nodes"] if matches_query(node)),
                             key=lambda node: len(node["path"]), reverse=True)[:5])
    return TopicContext(document_id, index, words, selected, preferred)


def canonical_scope(document_id: str, scope: dict | None):
    if not scope:
        return None
    context = resolve_topics(document_id, scope)
    if context is None or context.selected is None:
        raise ValueError("Select a topic from the uploaded PDF's outline.")
    node = context.selected
    return {"id": node["id"], "title": node["title"], "documentId": document_id,
            "page": node["start"][0], "topic_path": node["path"]}


def source_in_scope(source, scope, contexts=None) -> bool:
    if not scope:
        return True
    if scope.get("documentId") and scope["documentId"] != source.document_id:
        return False
    contexts = contexts if contexts is not None else {}
    if source.document_id not in contexts:
        contexts[source.document_id] = resolve_topics(source.document_id, scope)
    context = contexts[source.document_id]
    return context is not None and context.allows_quote(source.page, source.quote)
