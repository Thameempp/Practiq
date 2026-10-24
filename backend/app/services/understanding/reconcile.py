from copy import deepcopy

from app.orchestration.runtime import check_active
from app.services.topics.anchors import heading_position
from app.services.understanding.kinds import section_kind
from app.services.understanding.page_models import MapIssue


def reconcile_hierarchy(hierarchy: list[dict], pages: list[dict]) -> tuple[list, list]:
    """Recheck uncertain outline page claims against nearby original text."""
    result, issues = deepcopy(hierarchy), []
    texts = {page["page"]: page["text"] for page in pages}
    toc_pages = {page["page"] for page in pages if any(line.strip().casefold() in
                 {"contents", "table of contents"} for line in page["text"].splitlines()[:30])}


    def visit(nodes):
        for node in nodes:
            check_active()
            page, title = node.get("page"), node.get("title", "")
            node.pop("structureUncertain", None)


            def located(number):
                return (number not in toc_pages or section_kind(title) == "table_of_contents") and heading_position(title, texts.get(number, "")) is not None
            if isinstance(page, int) and not located(page):
                matches = [p for p in range(max(1, page - 2), min(len(pages), page + 2) + 1)
                           if located(p)]
                if len(matches) == 1:
                    actual = matches[0]
                    node.update(page=actual, pageLabel=f"p. {actual}", declaredPage=page)
                    issues.append(MapIssue(code="heading_page_mismatch", pdf_page=actual,
                        message=f"Outline heading '{title}' declared PDF page {page}; found on {actual}."))
                else:
                    node["structureUncertain"] = True
                    issues.append(MapIssue(code="unconfirmed_heading", pdf_page=page,
                        message=f"Heading '{title}' could not be uniquely confirmed near its declared page."))
            visit(node.get("children", []))
    visit(result)
    return result, issues
