import re

SPECIAL = {
    "table of contents": "table_of_contents", "contents": "table_of_contents",
    "preface": "front_matter", "acknowledgements": "front_matter",
    "acknowledgments": "front_matter", "abstract": "front_matter",
    "learning objectives": "learning_material", "introduction": "introduction",
    "conclusion": "conclusion", "conclusions": "conclusion", "summary": "summary",
    "references": "references", "bibliography": "bibliography", "glossary": "glossary",
    "index": "subject_index", "subject index": "subject_index",
    "exercises": "learning_material", "review questions": "learning_material",
    "key points": "learning_material", "examples": "learning_material",
}


def section_kind(title: str, depth: int = 1) -> str:
    text = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", title).strip().casefold().rstrip(":")
    for kind in ("appendix", "unit", "chapter", "part"):
        if re.match(rf"^{kind}(?:\s|$)", text):
            return kind
    if re.match(r"^\d+\s+", title) and depth == 1:
        return "chapter"
    if text in SPECIAL:
        return SPECIAL[text]
    return "section" if depth <= 2 else "subsection"
