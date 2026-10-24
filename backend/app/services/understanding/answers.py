from collections.abc import Callable

from app.services.understanding.selection import matching_sections, selected_topics
from app.services.understanding.models import DocumentMap
from app.services.understanding.query import StructureQuery
from app.services.understanding.section_models import DocumentSection


def structure_answer(document_map: DocumentMap, query: StructureQuery, link: Callable[[int, int], str]) -> str:
    title = f"## {document_map.filename}\n\n"
    sections = document_map.sections
    if query.kind == "count":
        if query.target == "page":
            return title + f"This PDF has **{document_map.total_pdf_pages} physical pages**. " + link(1, document_map.total_pdf_pages)
        matches = [s for s in sections if s.section_type == query.target]
        confirmed = sum(s.status == "confirmed" for s in matches)
        return title + (f"Detected **{confirmed} confirmed {query.target}(s)** and "
                        f"**{len(matches) - confirmed} candidate(s)**. Candidates have uncertain structure or boundaries. "
                        + link(1, document_map.total_pdf_pages))
    if query.kind == "topics":
        topics = selected_topics(document_map, query.target)
        lines = [f"- **{t.label}** — PDF page {t.pdf_page} ({t.status}) {link(t.pdf_page, t.pdf_page)}" for t in topics[:200]]
    elif query.kind == "chapter_for":
        found = [t for t in document_map.topics if query.target in t.label.casefold()]
        ids = {t.chapter_id for t in found if t.chapter_id}
        matches = [s for s in sections if s.section_id in ids]
        lines = [_section_line(s, link) for s in matches[:200]]
    else:
        matches = (matching_sections(document_map, query.target) if query.kind in {"has", "locate"}
                   else [s for s in sections if not query.target or s.section_type == query.target])
        lines = [_section_line(s, link) for s in matches[:200]]
    if not lines:
        return title + "That structure was **not detected** in the document map. This does not establish that it is absent."
    suffix = "\n\nShowing the first 200 matches; the document-map API contains the full inventory." if len(lines) == 200 else ""
    return title + "\n".join(lines) + suffix


def _section_line(section: DocumentSection, link: Callable[[int, int], str]) -> str:
    if not section.start_page:
        return f"- **{section.title}** — location uncertain."
    end = section.end_page or section.start_page
    pages = str(section.start_page) if end == section.start_page else f"{section.start_page}–{end}"
    printed = f", printed page {section.printed_page}" if section.printed_page else ""
    return f"- **{section.title}** — PDF pages {pages}{printed} ({section.status}) {link(section.start_page, end)}"
