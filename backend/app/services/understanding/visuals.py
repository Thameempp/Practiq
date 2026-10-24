import re
from pymupdf import Page

from app.services.understanding.page_models import PageElement, MapIssue

CAPTION = re.compile(r"^(figure|fig\.?|table|chart|diagram|equation|eq\.?)\s+\w*[\d]", re.I)


def page_elements(page: Page, blocks: list[dict], images: list[dict], drawings: list[dict]) -> tuple[list[PageElement], list[MapIssue]]:
    elements, issues = [], []
    for image in images[:100]:
        elements.append(PageElement(kind="image", status="confirmed", bbox=list(image["bbox"])))
    for block in blocks:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            match = CAPTION.match(text)
            if match:
                kind = "table" if match[1].lower() == "table" else "figure"
                elements.append(PageElement(kind=kind, bbox=list(line["bbox"]), text=text[:500]))
            elif "=" in text and re.search(r"\d|[α-ωΑ-Ω∫∑]", text):
                elements.append(PageElement(kind="equation", bbox=list(line["bbox"]), text=text[:500]))
    if drawings:
        elements.append(PageElement(kind="vector_graphics"))
        try:
            for table in page.find_tables(paths=drawings).tables[:100]:
                elements.append(PageElement(kind="table", bbox=list(table.bbox)))
        except (AttributeError, RuntimeError, ValueError):
            issues.append(MapIssue(code="table_detection_unavailable", message="Table geometry could not be inspected.", pdf_page=page.number + 1))
    if len(images) > 100 or len(elements) > 200:
        issues.append(MapIssue(code="visual_inventory_truncated", message="Dense visual inventory was capped; visual coverage is incomplete.", pdf_page=page.number + 1))
    return elements[:200], issues
