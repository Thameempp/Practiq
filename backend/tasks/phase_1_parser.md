# Phase 1 — Smart PDF Parser (`parser.py`)

## Goal

Replace the current `loader.py` plain text extraction with a **rich, structured extraction** layer.
This is the most critical phase — every other phase depends on the data this produces.

The parser must:
- Use **PyMuPDF** to extract text with font size, bold/italic flags, and bounding boxes
- **Detect scanned/image pages** where PyMuPDF finds little or no text
- Fall back to **PaddleOCR** on those pages
- Return a **unified data shape** regardless of which tool was used

---

## File to Create

```
backend/src/services/parser.py
```

---

## Step 1 — Install Dependencies

You already have `pymupdf`. Install PaddleOCR:

```bash
pip install paddlepaddle paddleocr opencv-python-headless
```

> **Note:** `paddlepaddle` is the CPU version. First run will download ~100MB of OCR models automatically.  
> After that, it's fast.

---

## Step 2 — Understand PyMuPDF `get_text("dict")`

This is the key change from the current `get_text("text")`.

When you call `page.get_text("dict")`, PyMuPDF returns a nested structure like this:

```python
{
  "blocks": [
    {
      "type": 0,          # 0 = text block, 1 = image block
      "bbox": [x0, y0, x1, y1],
      "lines": [
        {
          "spans": [
            {
              "text": "Activation Functions",
              "size": 18.0,        # font size
              "flags": 20,         # bitmask: bold, italic, etc.
              "font": "Arial-Bold",
              "bbox": [x0, y0, x1, y1],
              "color": 0
            }
          ]
        }
      ]
    }
  ]
}
```

### Understanding `flags` bitmask

The `flags` field is a bitmask integer. Use bitwise AND to check:

| Flag | Bit | Python check |
|------|-----|--------------|
| Superscript | 1 | `flags & 1` |
| Italic | 2 | `flags & 2` |
| Serif | 4 | `flags & 4` |
| Monospace | 8 | `flags & 8` |
| **Bold** | **16** | `flags & 16` |

So `flags = 20` means: **Bold (16) + Serif (4)** → `20 & 16 = 16` (truthy → bold).

---

## Step 3 — Understand the Scanned Page Detection Logic

Not every page in a PDF has selectable text. Scanned books/papers are images.

**Detection strategy:**

```
Extract text from page using PyMuPDF
Count the words in that text
If word count < MIN_THRESHOLD (e.g. 30 words):
    → This page is likely scanned/image-based
    → Run PaddleOCR on a rendered image of this page
Else:
    → Use PyMuPDF data directly
```

To render a page as an image for OCR:
```python
mat = pymupdf.Matrix(2, 2)   # 2x zoom for better OCR accuracy
pix = page.get_pixmap(matrix=mat)
img_bytes = pix.tobytes("png")
# Pass img_bytes to PaddleOCR
```

---

## Step 4 — Understand PaddleOCR Output

PaddleOCR returns results in this shape:

```python
result = ocr.ocr(img_array, cls=True)

# result is a list of pages, each page is a list of text lines:
# [ [ bbox_points, (text, confidence) ], ... ]

# Example:
[
  [
    [[72, 120], [310, 120], [310, 150], [72, 150]],   # 4 corner points
    ("Activation Functions", 0.97)                    # (text, confidence)
  ],
  ...
]
```

**Converting the 4-corner bbox to a flat [x0, y0, x1, y1]:**
```python
points = line[0]
x0 = min(p[0] for p in points)
y0 = min(p[1] for p in points)
x1 = max(p[0] for p in points)
y1 = max(p[1] for p in points)
```

---

## Step 5 — The Unified Data Shape

Both PyMuPDF and PaddleOCR paths must return the **same shape** so the next phases don't need to care which tool was used.

### For a PyMuPDF page:

```python
{
    "page": 1,
    "source": "pymupdf",
    "text": "full plain text of the page",
    "blocks": [
        {
            "text": "3.2 Activation Functions",
            "font_size": 18.0,
            "bold": True,
            "italic": False,
            "bbox": [70.0, 120.0, 300.0, 145.0],
            "block_type": "text"     # or "image"
        }
    ],
    "images": [
        {
            "bbox": [x0, y0, x1, y1],
            "index": 0               # image index on the page
        }
    ]
}
```

### For a PaddleOCR page:

```python
{
    "page": 1,
    "source": "paddleocr",
    "text": "full plain text joined from OCR lines",
    "blocks": [
        {
            "text": "Activation Functions",
            "font_size": None,       # OCR doesn't give font size
            "bold": None,            # OCR doesn't give bold info
            "italic": None,
            "bbox": [72, 120, 310, 150],
            "confidence": 0.97,
            "block_type": "text"
        }
    ],
    "images": []                     # no image metadata from OCR path
}
```

> **Why keep `None` instead of `False`?**  
> So the structure detector in Phase 2 knows the difference between  
> "this text is not bold" vs "we don't know if it's bold (OCR page)".

---

## Step 6 — Config Values to Add

In `backend/src/core/config.py`, add:

```python
MIN_TEXT_WORDS_FOR_PYMUPDF: int = 30
OCR_CONFIDENCE_THRESHOLD: float = 0.6
OCR_RENDER_SCALE: int = 2           # zoom factor for page-to-image rendering
```

---

## Step 7 — Function Signatures to Implement

```python
# parser.py

def extract_page_pymupdf(page, page_number: int) -> dict:
    """
    Use PyMuPDF to extract structured blocks with font info.
    Returns a page_data dict with source="pymupdf".
    """

def extract_page_paddleocr(page, page_number: int, ocr_engine) -> dict:
    """
    Render the page to an image, run PaddleOCR on it.
    Returns a page_data dict with source="paddleocr".
    Filter out blocks below OCR_CONFIDENCE_THRESHOLD.
    """

def is_text_sufficient(page_data: dict) -> bool:
    """
    Check if PyMuPDF extracted enough text.
    Count words in page_data["text"].
    Return True if word count >= MIN_TEXT_WORDS_FOR_PYMUPDF.
    """

def parse_pdf(pdf_path: str) -> list[dict]:
    """
    Main entry point.
    Opens the PDF, iterates pages, decides PyMuPDF vs OCR per page.
    Returns list of page_data dicts.
    """
```

---

## Step 8 — Update `loader.py`

After `parser.py` is ready, update `loader.py` to use it:

```python
# Replace the current content of loader.py with:
from src.services.parser import parse_pdf
from src.core.config import settings

path = settings.DATA_DIR / "computer_science_sample.pdf"

pages = parse_pdf(str(path))

# Keep backward compatibility: flatten into documents list
documents = []
page_count = len(pages)

for page_data in pages:
    documents.append({
        "page": page_data["page"],
        "text": page_data["text"],
        "source": page_data["source"]
    })
```

---

## What to Test After This Phase

```python
# Quick test script — run from backend/ directory
from src.services.parser import parse_pdf

pages = parse_pdf("data/computer_science_sample.pdf")

for p in pages[:3]:    # check first 3 pages
    print(f"\n--- Page {p['page']} | source: {p['source']} ---")
    print(f"  Block count: {len(p['blocks'])}")
    print(f"  Image count: {len(p['images'])}")
    for b in p['blocks'][:2]:   # first 2 blocks
        print(f"  [{b['font_size']}pt bold={b['bold']}] {b['text'][:60]}")
```

Expected output for a native PDF:
```
--- Page 1 | source: pymupdf ---
  Block count: 12
  Image count: 1
  [24.0pt bold=True] Chapter 1: Introduction
  [11.0pt bold=False] This chapter introduces the fundamental concepts...
```

---

## Common Mistakes to Avoid

| Mistake | Why it's a problem | Fix |
|---------|-------------------|-----|
| Using `get_text("text")` | Loses all font/layout info | Use `get_text("dict")` |
| Initializing PaddleOCR inside the page loop | Re-downloads models each call | Initialize OCR once, pass to function |
| Keeping all OCR results regardless of confidence | Garbage text pollutes structure detection | Filter with `OCR_CONFIDENCE_THRESHOLD` |
| Not handling empty pages | Will crash structure detector | Return empty blocks list for empty pages |

---

## Done when

- [ ] `parser.py` exists with all 4 functions
- [ ] `parse_pdf()` correctly chooses PyMuPDF vs PaddleOCR per page
- [ ] `loader.py` updated to call `parse_pdf()`
- [ ] Test script runs and shows block/font data for first 3 pages
- [ ] Config values added to `config.py`
