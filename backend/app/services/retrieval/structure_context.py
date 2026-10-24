"""Use structural hints while retaining canonical scope and original source text."""

from itertools import zip_longest

from app.services.retrieval.corpus import original_chunks
from app.services.topics.context import TopicContext
from app.services.understanding.models import DocumentMap
from app.services.understanding.section_models import DocumentTopic


class StructureContext(TopicContext):
    def __init__(self, context: TopicContext, mapped: DocumentMap, matched: tuple[DocumentTopic, ...]):
        super().__init__(context.document_id, context.index, context.words,
                         context.selected, context.preferred)
        self.document_map, self.matched = mapped, matched
        self.sections = {section.section_id: section for section in mapped.sections}
        self.pages = {page.pdf_page: page for page in mapped.pages}
        self.depths = {node["id"]: len(node["path"]) for node in self.index["nodes"]}


    def apply(self, chunks: list[dict]) -> list[dict]:
        result = [{**chunk, "metadata": dict(chunk.get("metadata") or {})}
                  for chunk in super().apply(chunks)]
        for chunk in result:
            metadata = chunk["metadata"]
            section = max((self.sections[node_id] for node_id in metadata.get("topic_ids", [])
                           if node_id in self.sections),
                          key=lambda s: self.depths.get(s.section_id, 0), default=None)
            page = self.pages.get(metadata.get("page_start", metadata.get("page")))
            metadata["document_structure"] = {
                "section_type": section.section_type if section else None,
                "status": section.status if section else "uncertain",
                "confidence": section.confidence if section else 0,
                "printed_page": page.printed_page if page else None,
                "page_quality": page.quality if page else "unknown",
                "needs_ocr": page.needs_ocr if page else False,
            }
        return result


    def seed_candidates(self, limit: int) -> list[dict]:
        if not self.matched or limit < 1:
            return []
        groups = []
        for topic in self.matched:
            ids = topic.chunk_ids
            count = min(limit, len(ids))
            positions = [round(i * (len(ids) - 1) / max(1, count - 1)) for i in range(count)]
            groups.append([ids[position] for position in positions])
        ids = list(dict.fromkeys(item for row in zip_longest(*groups)
                                 for item in row if item))[:limit]
        original = {c["id"]: c for c in original_chunks(self.document_id) or []}
        return self.apply([original[item] for item in ids if item in original])
