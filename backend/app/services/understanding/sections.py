import re

from app.services.topics.anchors import token
from app.services.understanding.kinds import SPECIAL, section_kind
from app.services.understanding.section_models import DocumentSection
from app.services.understanding.page_models import PageInventory


def map_sections(index: dict, pages: list[dict], inventory: list[PageInventory]) -> list[DocumentSection]:
    total = len(inventory)
    texts = {page["page"]: page["text"].split() for page in pages}
    labels = {p.pdf_page: p.printed_page for p in inventory}
    result = []
    for node in index["nodes"]:
        page, word = node["start"]
        valid = 1 <= page <= total
        end = min(total, node["end"][0] - (node["end"][1] == 0))
        status = "confirmed" if node["reliable"] and valid and not node.get("inferred") else "probable" if node["anchored"] and valid else "uncertain"
        kind = section_kind(node["title"], len(node["path"]))
        parent = next((s for s in result if s.section_id == node["parent_id"]), None)
        while parent:
            if kind in {"chapter", "unit", "part"} and parent.section_type in {"appendix", "references", "bibliography", "subject_index"}:
                kind = "section"
            parent = next((s for s in result if s.section_id == parent.parent_section_id), None)
        result.append(DocumentSection(section_id=node["id"], title=node["title"],
            section_type=kind,
            roles=[SPECIAL[plain]] if (plain := token(re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", node["title"]))) in SPECIAL else [],
            start_page=page if valid else None, end_page=max(page, end) if valid else None,
            printed_page=labels.get(page), parent_section_id=node["parent_id"], status=status,
            confidence={"confirmed": .95, "probable": .65, "uncertain": .25}[status],
            evidence=" ".join(texts.get(page, [])[word:word + 24]) if node["anchored"] else ""))
    known = {(token(s.title), s.start_page) for s in result}
    for page in pages:
        for position, line in enumerate(page["text"].splitlines()):
            text = line.strip()
            kind = SPECIAL.get(token(text))
            if not kind or (token(text), page["page"]) in known:
                continue
            if kind == "subject_index" and page["page"] <= total // 2:
                continue
            result.append(DocumentSection(section_id=f"special-{page['page']}-{position}", title=text,
                section_type=kind, start_page=page["page"], printed_page=labels.get(page["page"]),
                status="probable", confidence=.65, evidence=text))
            known.add((token(text), page["page"]))
    for section in result:
        section.children = [s.section_id for s in result if s.parent_section_id == section.section_id]
    return result
