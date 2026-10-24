"""Consult the understanding agent's revision-checked map before evidence search."""

import re

from fastapi import HTTPException

from app.services.pdf_source import registered_document
from app.services.retrieval.lexical import terms
from app.services.retrieval.structure_context import StructureContext
from app.services.retrieval.topics import resolve_topics
from app.services.topics.context import TopicContext
from app.services.understanding.models import DocumentMap
from app.services.understanding.service import document_map
from app.services.understanding.section_models import DocumentTopic


def resolve_retrieval_context(document_id: str, scope=None, question: str = "") -> TopicContext | None:
    document = registered_document(document_id)
    mapped = None
    if document:
        try:
            mapped = document_map(document_id, document.knowledge_base_id)
        except HTTPException as error:
            if error.status_code != 404:
                raise
    context = resolve_topics(document_id, scope, question)
    if mapped is None:
        return context
    context = context or TopicContext(document_id, {"nodes": [], "chunks": []}, {})
    matched = match_topics(mapped, question, context.selected)
    ids = {topic.section_id for topic in matched}
    nodes = [node for node in context.index["nodes"] if node["reliable"] and node["id"] in ids]
    existing = [node for node in context.preferred
                if not _reference_label(node["title"]) or node["id"] in ids]
    preferred = {node["id"]: node for node in [*nodes, *existing]}
    context.preferred = tuple(preferred.values())[:5]
    return StructureContext(context, mapped, matched)


def match_topics(mapped: DocumentMap, question: str, selected: dict | None) -> tuple[DocumentTopic, ...]:
    query = set(terms(question))
    references = set(re.findall(r"\b(chapter|unit|part)\s+(\d+)\b", question.casefold()))
    sections = set()
    for section in mapped.sections:
        number = re.match(r"(?:chapter\s+|unit\s+|part\s+)?(\d+)\b", section.title.casefold())
        if (section.status == "confirmed" and number
                and (section.section_type, number[1]) in references):
            sections.add(section.section_id)
    if selected:
        sections.add(selected["id"])
    matched = [topic for topic in mapped.topics if topic.status in {"confirmed", "probable"}
               and (topic.section_id in sections and topic.kind == "heading"
                    or not _reference_label(topic.label)
                    and bool(words := set(terms(topic.label))) and words.issubset(query))]
    return tuple(sorted(matched, key=lambda t: (t.section_id in sections,
                       t.kind == "definition", len(terms(t.label))), reverse=True)[:5])


def _reference_label(text: str) -> bool:
    return bool(re.fullmatch(r"(?:chapter|unit|part)\s+\d+[.:]?", text.strip(), re.I))
