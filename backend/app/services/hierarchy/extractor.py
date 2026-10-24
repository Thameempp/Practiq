import pymupdf

from app.services.hierarchy.classifier import build_style_profile
from app.services.hierarchy.line_extractor import collect_lines
from app.services.hierarchy.toc_hierarchy import toc_hierarchy_for
from app.services.hierarchy.tree_builder import build_hierarchy
from app.services.page_noise import drop_repeated_lines


def extract_hierarchy(file_path: str) -> list[dict]:
    """Extract frontend-ready document hierarchy from a PDF file."""
    doc = pymupdf.open(file_path)
    try:
        outline = toc_hierarchy_for(doc)
        if outline:
            return outline
        lines = drop_repeated_lines(collect_lines(doc), len(doc))
    finally:
        doc.close()

    if not lines:
        return []

    profile = build_style_profile(lines)
    return build_hierarchy(lines, profile)
