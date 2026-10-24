from app.services.hierarchy.classifier import StyleProfile, classify_line
from app.services.hierarchy.patterns import (
    RE_BULLET_PREFIX,
    RE_LEADING_LIST_NUMBER,
    clean_text,
)


def build_hierarchy(lines: list[dict], profile: StyleProfile) -> list[dict]:
    """Build nested hierarchy nodes from classified PDF lines."""
    if not lines:
        return []

    roots: list[dict] = []
    stack: list[tuple[int, dict]] = []
    excerpt_buffers: dict[str, list[str]] = {}
    uid = [0]

    for line in lines:
        level = classify_line(line, profile)

        if level is None:
            _append_excerpt(stack, excerpt_buffers, line["text"])
            continue

        node = _new_node(uid, line, level)
        _attach_node(roots, stack, level, node)

        if node["summary"]:
            excerpt_buffers.setdefault(node["id"], []).append(node["summary"])

    _attach_excerpts(roots, excerpt_buffers)
    return _dedupe_tree(roots)


def _append_excerpt(
    stack: list[tuple[int, dict]],
    excerpt_buffers: dict[str, list[str]],
    text: str,
) -> None:
    if not stack:
        return
    target = stack[-1][1]
    excerpt_buffers.setdefault(target["id"], []).append(text)


def _attach_node(
    roots: list[dict],
    stack: list[tuple[int, dict]],
    level: int,
    node: dict,
) -> None:
    while stack and stack[-1][0] >= level:
        stack.pop()

    if stack:
        stack[-1][1]["children"].append(node)
    else:
        roots.append(node)

    stack.append((level, node))


def _new_node(uid: list[int], line: dict, level: int) -> dict:
    uid[0] += 1
    title = _node_title(line["text"], level)
    node_type = _node_type(level)
    return {
        "id": f"{node_type}-{uid[0]}",
        "title": title,
        "type": node_type,
        "page": line["page"],
        "pageLabel": f"p. {line['page']}",
        "summary": _summary_from_line(line["text"], title),
        "excerpt": "",
        "children": [],
    }


def _node_title(text: str, level: int) -> str:
    text = RE_BULLET_PREFIX.sub("", text).strip()

    if level >= 4 and ":" in text:
        return text.split(":", 1)[0].strip()

    return text.rstrip(":").strip()


def _node_type(level: int) -> str:
    return {
        1: "document",
        2: "section",
        3: "subsection",
        4: "topic",
        5: "subtopic",
    }.get(level, "topic")


def _summary_from_line(text: str, title: str) -> str:
    cleaned = RE_BULLET_PREFIX.sub("", text).strip()
    cleaned = RE_LEADING_LIST_NUMBER.sub(r"\2", cleaned).strip()
    if ":" in cleaned:
        summary = cleaned.split(":", 1)[1].strip()
        return summary if summary else ""
    return "" if cleaned == title else cleaned


def _attach_excerpts(nodes: list[dict], excerpt_buffers: dict[str, list[str]]) -> None:
    for node in nodes:
        excerpt = clean_text(" ".join(excerpt_buffers.get(node["id"], [])))
        if excerpt:
            node["excerpt"] = excerpt[:900]
        _attach_excerpts(node.get("children", []), excerpt_buffers)


def _dedupe_tree(nodes: list[dict]) -> list[dict]:
    seen: set[tuple[str, int]] = set()
    result: list[dict] = []

    for node in nodes:
        key = (node["title"].lower(), node["page"])
        if key in seen:
            continue
        seen.add(key)
        result.append({**node, "children": _dedupe_tree(node.get("children", []))})

    return result
