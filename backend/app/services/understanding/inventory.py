from hashlib import sha256

import pymupdf

from app.orchestration.runtime import check_active
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.services.understanding.labels import printed_label
from app.services.understanding.page_models import MapIssue, PageInventory
from app.services.understanding.visuals import page_elements


def inspect_pages(pdf: pymupdf.Document) -> tuple[list[PageInventory], list[dict]]:
    inventory, texts, seen = [], [], {}
    has_labels = bool(pdf.get_page_labels())
    for number in range(len(pdf)):
        check_active()
        try:
            page = pdf[number]
            text = page.get_text("text", sort=True)
            blocks = page.get_text("dict", flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)["blocks"]
            images, drawings = page.get_image_info(hashes=True), page.get_drawings()
            elements, issues = page_elements(page, blocks, images, drawings)
            label, label_source = printed_label(page, blocks, has_labels)
            readable = len(text.strip()) >= 20
            quality = "readable" if readable or text.strip() and not images and not drawings else "scanned_candidate" if images else "unreadable" if drawings else "blank_candidate"
            record = PageInventory(pdf_page=number + 1, printed_page=label, printed_label_source=label_source,
                width=page.rect.width, height=page.rect.height, rotation=page.rotation,
                text_chars=len(text.strip()), image_count=len(images), vector_count=len(drawings),
                needs_ocr=bool(images) and not readable, quality=quality, elements=elements, issues=issues)
            fingerprint = sha256((" ".join(text.split()) + str(drawings) + str([(i.get("digest", b"").hex(), i["bbox"]) for i in images])).encode()).hexdigest()
            if readable or images:
                record.duplicate_of = seen.get(fingerprint)
                seen.setdefault(fingerprint, number + 1)
            if record.duplicate_of:
                record.issues.append(MapIssue(code="duplicate_page_candidate", message=f"Page content matches PDF page {record.duplicate_of}; repetition may be intentional.", pdf_page=number + 1))
            if "�" in text:
                record.issues.append(MapIssue(code="replacement_characters", message="Extracted text contains unreadable characters.", pdf_page=number + 1))
            if quality != "readable":
                record.issues.append(MapIssue(code=quality, message="This page needs inspection; lack of text does not prove it is blank.", pdf_page=number + 1))
            inventory.append(record)
            texts.append({"page": number + 1, "text": text})
        except (TaskCancelled, TaskDeadline):
            raise
        except (RuntimeError, ValueError) as error:
            inventory.append(PageInventory(pdf_page=number + 1, quality="failed", issues=[
                MapIssue(code="extraction_error", message=f"Page inspection failed ({type(error).__name__}).", pdf_page=number + 1)]))
            texts.append({"page": number + 1, "text": ""})
    return inventory, texts
