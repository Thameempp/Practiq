import re

from app.documents.matching import normalize


def section_range(document, chapter_reference=None, scope=None):
    if not chapter_reference and not scope:
        return None
    if not document.hierarchy:
        raise ValueError("This PDF has no stored outline. Re-upload it to enable reliable chapter summaries.")
    target_id = (scope or {}).get("id")
    target_title = normalize((scope or {}).get("title", ""))
    target = normalize(chapter_reference or "")
    matches = []


    def visit(nodes, parent_end):
        for index, node in enumerate(nodes):
            start = node.get("page")
            following = nodes[index + 1].get("page") if index + 1 < len(nodes) else None
            end = following - 1 if isinstance(following, int) else parent_end
            title = normalize(node.get("title", ""))
            chapter = bool(target and (title.startswith(f"chapter {target} ") or title == f"chapter {target}"
                                      or re.match(rf"^{re.escape(target)}(?:\s|$)", title)))
            selected = (node.get("id") == target_id if target_id else title == target_title and bool(title))
            if chapter or scope and selected and not chapter_reference:
                if isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= document.pages:
                    matches.append((start, end))
            visit(node.get("children", []), end)
    visit(document.hierarchy, document.pages)
    unique = set(matches)
    if len(unique) != 1:
        raise ValueError("I could not reliably determine that chapter's page boundaries. Select a section from this PDF's outline.")
    return unique.pop()
