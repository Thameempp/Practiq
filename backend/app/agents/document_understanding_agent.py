"""Build a full-document structural map without generating a semantic summary."""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from app.agents.base import BaseAgent
from app.citations.documents import revision_of
from app.documents.models import Document
from app.services.page_noise import clean_pages
from app.services.hierarchy_extractor import extract_hierarchy
from app.services.topics.builder import build_topic_index
from app.services.topics.storage import signature
from app.services.understanding.inventory import inspect_pages
from app.services.understanding.heading_fallback import inferred_headings
from app.services.understanding.models import DocumentMap
from app.services.understanding.reconcile import reconcile_hierarchy
from app.services.understanding.sections import map_sections
from app.services.understanding.section_models import DocumentSection
from app.services.understanding.topics import map_topics


@dataclass
class UnderstandingResult:
    document_map: DocumentMap
    hierarchy: list[dict]
    topic_index: dict


class DocumentUnderstandingAgent(BaseAgent[UnderstandingResult]):
    def understand(self, document: Document, *, pages: list[dict] | None = None) -> UnderstandingResult:
        return self.run(document, pages=pages)


    def _run(self, document: Document, *, pages: list[dict] | None = None) -> UnderstandingResult:
        path = Path(document.saved_path)
        before = revision_of(path)
        with pymupdf.open(path) as pdf:
            inventory, raw = inspect_pages(pdf)
            metadata, outline = pdf.metadata or {}, bool(pdf.get_toc())
            kind, language = pdf.xref_get_key(pdf.pdf_catalog(), "Lang")
        if revision_of(path) != before:
            raise ValueError("The PDF changed during analysis. Please try again.")
        pages = pages if pages is not None else clean_pages(raw)
        source_hierarchy = document.hierarchy or inferred_headings(pages) or extract_hierarchy(str(path))
        hierarchy, issues = reconcile_hierarchy(source_hierarchy, pages)
        index = build_topic_index(hierarchy, pages, len(inventory))
        sections = map_sections(index, pages, inventory)
        title = metadata.get("title", "").strip()
        if title and any(line.strip().casefold() == title.casefold() for line in raw[0]["text"].splitlines()):
            sections.append(DocumentSection(section_id="cover-title", title=title, section_type="front_matter",
                roles=["cover"], start_page=1, end_page=1, printed_page=inventory[0].printed_page,
                status="probable", confidence=.65, evidence=title))
        sections.sort(key=lambda s: (s.start_page or len(inventory) + 1, s.section_id))
        topics = map_topics(document.document_id, index, sections, pages)
        issues.extend(issue for page in inventory for issue in page.issues)
        uncertain = any(s.status != "confirmed" for s in sections) or bool(issues)
        toc = [s for s in sections if "table_of_contents" in [s.section_type, *s.roles]]
        subject = [s for s in sections if "subject_index" in [s.section_type, *s.roles]]
        result = DocumentMap(document_id=document.document_id, knowledge_base_id=document.knowledge_base_id,
            filename=document.filename, title=metadata.get("title") or None, author=metadata.get("author") or None,
            language=language if kind == "string" else None, total_pdf_pages=len(inventory), revision=before,
            hierarchy_signature=signature(hierarchy), topic_index_version=index["version"], embedded_outline=outline,
            has_table_of_contents=bool(toc), has_subject_index=bool(subject),
            table_of_contents_status=toc[0].status if toc else "not_found",
            subject_index_status=subject[0].status if subject else "not_found",
            pages=inventory, sections=sections, topics=topics, issues=issues,
            structure_status="failed" if all(p.quality == "failed" for p in inventory)
            else "partial" if uncertain or not sections else "complete")
        if revision_of(path) != before:
            raise ValueError("The PDF changed during analysis. Please try again.")
        return UnderstandingResult(result, hierarchy, index)
