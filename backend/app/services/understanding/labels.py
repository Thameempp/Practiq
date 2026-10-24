import re
from pymupdf import Page


def printed_label(page: Page, blocks: list[dict], has_labels: bool) -> tuple[str | None, str | None]:
    if has_labels:
        return page.get_label() or None, "pdf_labels"
    candidates = []
    for block in blocks:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if line["bbox"][1] >= page.rect.height * .88 and re.fullmatch(r"\d{1,5}|[ivxlcdmIVXLCDM]{1,12}", text):
                candidates.append(text)
    unique = set(candidates)
    return (unique.pop(), "footer") if len(unique) == 1 else (None, None)
