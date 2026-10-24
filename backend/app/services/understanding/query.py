import re
from dataclasses import dataclass

from app.services.understanding.kinds import SPECIAL


@dataclass(frozen=True)
class StructureQuery:
    kind: str
    target: str = ""


def structure_query(question: str) -> StructureQuery | None:
    text = question.strip().rstrip(".?!").casefold()
    count = re.search(r"\bhow many (?:physical |pdf )?(pages|chapters|units|sections|subsections)\b", text)
    if count:
        return StructureQuery("count", count[1].removesuffix("s"))
    topics = re.search(r"\b(?:list|show|what are)\b.*\b(?:topics|subtopics|sections)\b.*\b(chapter|unit)\s+(\d+|[ivxlcdm]+)\b", text)
    if topics:
        return StructureQuery("topics", f"{topics[1]} {topics[2]}")
    chapter = re.search(r"\bwhich (?:chapter|unit) (?:discusses|covers|contains)\s+(.+)", text)
    if chapter:
        return StructureQuery("chapter_for", chapter[1].strip('"'))
    page = re.search(r"\b(?:which|what) (?:pdf )?page (?:contains|covers|discusses|has|is)\s+(.+)", text)
    if page:
        return StructureQuery("locate", re.sub(r"\s+(?:on|in)(?: (?:this|the) (?:pdf|document))?$", "", page[1]).strip('"'))
    for name, kind in SPECIAL.items():
        if re.search(rf"\b{re.escape(name)}\b", text):
            if re.match(r"(?:does\b|is there\b|are there\b|has\b)", text):
                return StructureQuery("has", kind)
            if re.match(r"where (?:is|are)\b", text):
                return StructureQuery("locate", name)
    appendix = re.search(r"\bappendi(?:x|ces)\b", text)
    if appendix and re.match(r"(?:does\b|is there\b|are there\b|where\b)", text):
        return StructureQuery("has" if not text.startswith("where") else "locate", "appendix")
    if re.match(r"(?:list|show|what are)\b", text) and re.search(r"\b(?:chapters|units|outline|document structure|table of contents)\b", text):
        return StructureQuery("outline", "unit" if "units" in text else "chapter" if "chapters" in text else "")
    return None
