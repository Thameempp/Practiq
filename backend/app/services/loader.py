import pymupdf
from pathlib import Path

from app.services.page_noise import clean_pages


def load_pdf(file_path: str | Path):
    doc = pymupdf.open(file_path)

    page_count = len(doc)
    texts = [page.get_text("text", sort=True) for page in doc]
    doc.close()

    pages = clean_pages([{"page": number, "text": text} for number, text in enumerate(texts, 1)])
    return pages, page_count
