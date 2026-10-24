import re

from app.services.topics.context import overlap
from app.services.understanding.section_models import DocumentSection, DocumentTopic

NON_TOPICS = {"front_matter", "table_of_contents", "subject_index", "references", "bibliography", "glossary"}
DEFINITION = re.compile(r"\b([A-Za-z][\w -]{1,55}?)\s+(?:is defined as|refers to)\s+[^.\n]+[.]?", re.I)


def map_topics(document_id: str, index: dict, sections: list[DocumentSection], pages: list[dict]) -> list[DocumentTopic]:
    result, by_id = [], {s.section_id: s for s in sections}


    def chapter(section: DocumentSection | None) -> str | None:
        seen = set()
        while section and section.section_id not in seen:
            seen.add(section.section_id)
            if section.section_type in {"chapter", "unit", "part"}:
                return section.section_id
            section = by_id.get(section.parent_section_id)
        return None

    for node in index["nodes"]:
        section = by_id[node["id"]]
        if section.section_type in NON_TOPICS or not section.start_page:
            continue
        ids = [f"{document_id}-chunk-{c['index']}" for c in index["chunks"] if overlap(c, node) != (0, 0)]
        result.append(DocumentTopic(topic_id=f"heading:{section.section_id}",
            label=re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", section.title), section_id=section.section_id,
            chapter_id=chapter(section), pdf_page=section.start_page, status=section.status,
            evidence=section.evidence, chunk_ids=ids))
    for page in pages:
        for match in DEFINITION.finditer(page["text"]):
            word = len(page["text"][:match.start()].split())
            candidates = [n for n in index["nodes"] if n["reliable"]
                          and overlap({"page": page["page"], "start": word, "end": word + 1}, n) != (0, 0)]
            node = max(candidates, key=lambda n: len(n["path"]), default=None)
            section = by_id.get(node["id"]) if node else None
            ids = [f"{document_id}-chunk-{c['index']}" for c in index["chunks"]
                   if c["page"] == page["page"] and c["start"] <= word < c["end"]]
            result.append(DocumentTopic(topic_id=f"definition:{page['page']}:{word}", label=match[1].strip(),
                pdf_page=page["page"], kind="definition", evidence=match[0][:500], chunk_ids=ids,
                section_id=section.section_id if section else None, chapter_id=chapter(section)))
    return result
