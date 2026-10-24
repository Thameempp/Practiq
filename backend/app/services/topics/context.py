from dataclasses import dataclass
import unicodedata

from app.services.chunk_ids import chunk_index_of


def overlap(location: dict, node: dict) -> tuple[int, int]:
    page = location["page"]
    start, end = node["start"], node["end"]
    left = max(location["start"], start[1] if page == start[0] else 0)
    right = min(location["end"], end[1] if page == end[0] else location["end"])
    return (left, right) if start[0] <= page <= end[0] and left < right else (0, 0)


@dataclass
class TopicContext:
    document_id: str
    index: dict
    words: dict
    selected: dict | None = None
    preferred: tuple = ()


    def apply(self, chunks: list[dict]) -> list[dict]:
        locations = {item["index"]: item for item in self.index["chunks"]}
        result = []
        for chunk in chunks:
            metadata = chunk.get("metadata") or {}
            if metadata.get("document_id") != self.document_id:
                continue
            position = chunk_index_of(chunk)
            if position is None:
                suffix = str(chunk.get("id", "")).removeprefix(f"{self.document_id}-chunk-")
                position = int(suffix) if suffix.isdigit() else None
            location = locations.get(position)
            page = metadata.get("page_start", metadata.get("page", chunk.get("page_start")))
            if not location or page != location["page"]:
                if not self.selected:
                    result.append(chunk)
                continue
            text = str(metadata.get("text") or chunk.get("text") or "").split()
            base = metadata.get("topic_word_start", location["start"])
            if location["page"] in self.words:
                text = self.words[location["page"]][location["start"]:location["end"]]
                base = location["start"]
            current = {**location, "start": base, "end": base + len(text)}
            left, right = overlap(current, self.selected) if self.selected else (base, base + len(text))
            if left >= right:
                continue
            text = " ".join(text[left - base:right - base])
            visible = {**current, "start": left, "end": right}
            topics = [node for node in self.index["nodes"] if node["reliable"] and overlap(visible, node) != (0, 0)]
            preferred = next((node for node in self.preferred if node in topics), None)
            primary = self.selected or preferred or max(topics, key=lambda n: len(n["path"]), default=None)
            result.append({**chunk, "text": text, "metadata": {**metadata, "text": text,
                "topic_word_start": left, "topic_path": primary["path"] if primary else [],
                "topic_ids": [node["id"] for node in topics]}})
        return result


    def vector_filter(self) -> dict:
        if not self.selected:
            return {}
        indices = [c["index"] for c in self.index["chunks"] if overlap(c, self.selected) != (0, 0)]
        return {"$and": [{"chunk_index": {"$gte": min(indices)}},
                         {"chunk_index": {"$lte": max(indices)}}]} if indices else {"chunk_index": {"$lt": 0}}


    def allows_quote(self, page: int, quote: str) -> bool:
        if not self.selected:
            return True
        words = self.words.get(page, [])
        left, right = overlap({"page": page, "start": 0, "end": len(words)}, self.selected)
        normalize = lambda value: " ".join(unicodedata.normalize("NFC", value).split()).casefold()
        return bool(quote.strip()) and normalize(quote) in normalize(" ".join(words[left:right]))
