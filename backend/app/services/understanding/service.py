from app.agents.document_understanding_agent import DocumentUnderstandingAgent
from app.citations.documents import require_pdf, revision_of
from app.documents.repository import save_document
from app.documents.models import Document
from app.services.hierarchy_extractor import extract_hierarchy
from app.services.topics.builder import TOPIC_VERSION
from app.services.topics.storage import save_topics, signature
from app.services.understanding.models import DocumentMap, MAP_VERSION
from app.services.understanding.storage import read_map, save_map


def analyze_document(document: Document, *, pages: list[dict] | None = None) -> DocumentMap:
    result = DocumentUnderstandingAgent().understand(document, pages=pages)
    document.hierarchy = result.hierarchy
    document.pages = result.document_map.total_pdf_pages
    annotate_map(document.hierarchy, result.document_map)
    result.document_map.hierarchy_signature = signature(document.hierarchy)
    save_topics(document, pages, index=result.topic_index, revision=result.document_map.revision)
    save_map(result.document_map)
    return result.document_map


def document_map(document_id: str, knowledge_base_id: str = "local", *, refresh: bool = False) -> DocumentMap:
    document, path = require_pdf(document_id, knowledge_base_id)
    stored = read_map(document_id, knowledge_base_id)
    revision = revision_of(path)
    if (not refresh and stored and stored.revision == revision and stored.analysis_version == MAP_VERSION
            and stored.topic_index_version == TOPIC_VERSION
            and stored.hierarchy_signature == signature(document.hierarchy)):
        return stored
    document.saved_path = str(path)
    if stored and stored.revision != revision:
        document.hierarchy = extract_hierarchy(str(path))
    result = analyze_document(document)
    save_document(document)
    return result


def annotate_map(hierarchy: list[dict], document_map: DocumentMap) -> None:
    sections = {s.section_id: s for s in document_map.sections}


    def visit(nodes):
        for node in nodes:
            section = sections.get(node["id"])
            if section:
                node.update(endPage=section.end_page, structureStatus=section.status,
                            structureConfidence=section.confidence, printedPage=section.printed_page)
            visit(node.get("children", []))
    visit(hierarchy)
