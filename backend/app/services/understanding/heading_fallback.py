import re

from app.services.understanding.kinds import SPECIAL

NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)(?:[.)]?\s+)(\S.+)$")
NAMED = re.compile(r"^(?:chapter|unit|part|appendix)\s+[\w]+(?:\b|:)", re.I)


def inferred_headings(pages: list[dict]) -> list[dict]:
    """Conservative fallback for PDFs without an existing usable outline."""
    roots, stack, serial = [], [], 0
    for page in pages:
        lines = page["text"].splitlines()
        is_toc = any(line.strip().casefold() in {"contents", "table of contents"} for line in lines[:30])
        for line in lines:
            text = line.strip()
            if not text or len(text) > 100 or len(text.split()) > 12:
                continue
            numbered = NUMBERED.fullmatch(text)
            special = SPECIAL.get(text.casefold())
            if is_toc and special != "table_of_contents":
                continue
            if numbered and ("=" in text or text.endswith((".", "?", "!", ";")) or "..." in text):
                continue
            if not numbered and not special and not NAMED.match(text):
                continue
            level = len(numbered[1].split(".")) if numbered else 2 if special == "learning_material" and stack else 1
            serial += 1
            node = {"id": f"inferred-{serial}", "title": text,
                    "page": page["page"], "pageLabel": f"p. {page['page']}", "children": [], "structureInferred": True}
            while stack and stack[-1][0] >= level:
                stack.pop()
            (stack[-1][1]["children"] if stack else roots).append(node)
            stack.append((level, node))
    return roots
