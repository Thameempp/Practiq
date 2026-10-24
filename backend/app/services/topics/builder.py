from app.services.chunker import word_spans
from app.services.topics.anchors import heading_span

TOPIC_VERSION = 3


def build_topic_index(hierarchy: list[dict], pages: list[dict], page_count: int) -> dict:
    texts = {page["page"]: page["text"] for page in pages}
    nodes, cursors = [], {}


    def visit(branch, parent_id=None, path=()):
        for node in branch:
            page, title = node.get("page"), node.get("title", "")
            span = None if node.get("structureUncertain") else heading_span(title, texts.get(page, ""), cursors.get(page, 0))
            found = span[0] if span else None
            if span:
                cursors[page] = span[1]
            nodes.append({"id": node.get("id"), "parent_id": parent_id, "title": title,
                          "path": [*path, title], "start": [page or 0, found or 0],
                          "anchored": found is not None, "inferred": bool(node.get("structureInferred"))})
            visit(node.get("children", []), node.get("id"), (*path, title))
    visit(hierarchy)
    for i, node in enumerate(nodes):
        following = next((item for item in nodes[i + 1:] if len(item["path"]) <= len(node["path"])), None)
        node["end"] = following["start"] if following else [page_count + 1, 0]
        node["reliable"] = (node["anchored"] and (following is None or following["anchored"])
                            and tuple(node["start"]) < tuple(node["end"]))
    chunks = []
    for page in pages:
        for start, end in word_spans(len(page["text"].split())):
            chunks.append({"index": len(chunks), "page": page["page"], "start": start, "end": end})
    return {"version": TOPIC_VERSION, "nodes": nodes, "chunks": chunks}
