import pymupdf
from src.services.clean import clean_text
from src.core.config import settings

path = settings.DATA_DIR / "computer_science_sample.pdf"

doc = pymupdf.open(path)

page_count = doc.page_count
# print(f"Number of pages: {doc.page_count}")

documents = []

for page_number, page in enumerate(doc, start=1):
    page_text = page.get_text('text', sort=True)


    # Split into smaller chunks 
    words = clean_text(page_text)
    chunk_size = 20

    for start in range(0, len(words), chunk_size):
        chunk_words = words[start:start + chunk_size]

        if chunk_words:
            chunk = " ".join(chunk_words)

            documents.append({
                "page": page_number,
                "text": chunk
            })

doc.close()