import pymupdf
from pathlib import Path


def load_pdf(file_path: str | Path):
    doc = pymupdf.open(file_path)
    
    page_count = len(doc)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        pages.append({
            "page": page_number,
            "text": page.get_text("text", sort=True)
        })

        
    doc.close()
    return pages, page_count