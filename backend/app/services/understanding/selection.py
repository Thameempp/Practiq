import re

from app.services.topics.anchors import token
from app.services.understanding.models import DocumentMap
from app.services.understanding.section_models import DocumentSection, DocumentTopic


def matching_sections(document_map: DocumentMap, target: str) -> list[DocumentSection]:
    wanted = token(re.sub(r"^(?:the|a|an)\s+", "", target).strip('"'))
    numbered = re.fullmatch(r"(chapter|unit)\s+(\d+|[ivxlcdm]+)", wanted)
    result = []
    for section in document_map.sections:
        title = token(section.title)
        number_match = numbered and section.section_type == numbered[1] and re.match(
            rf"^(?:{numbered[1]}\s+)?{re.escape(numbered[2])}(?:[.)]?\s|$)", title)
        matches = bool(number_match) if numbered else wanted == section.section_type or wanted in section.roles or wanted in title
        if matches:
            result.append(section)
    return result


def selected_topics(document_map: DocumentMap, target: str) -> list[DocumentTopic]:
    roots = {s.section_id for s in matching_sections(document_map, target)}
    ids = set(roots)
    for _ in range(len(document_map.sections)):
        children = {s.section_id for s in document_map.sections if s.parent_section_id in ids}
        if children.issubset(ids):
            break
        ids.update(children)
    return [t for t in document_map.topics if t.section_id in ids and t.section_id not in roots]
