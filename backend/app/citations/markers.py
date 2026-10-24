"""Validate source markers incrementally before emitting linked citations."""

from collections.abc import Iterator

from app.citations.catalog import emit_metadata, publish_sources


class CitationMarkers:
    def __init__(self, sources: dict) -> None:
        self.sources = sources
        self.pending = ""


    def feed(self, text: str, *, final: bool = False) -> str:
        self.pending += text
        output = []
        while self.pending:
            starts = [(self.pending.find(opener), opener, closer)
                      for opener, closer in (("[[", "]]"), ("【", "】"))]
            starts = [item for item in starts if item[0] >= 0]
            if not starts:
                keep = 1 if not final and self.pending.endswith("[") else 0
                output.append(self.pending[:-keep] if keep else self.pending)
                self.pending = self.pending[-keep:] if keep else ""
                break
            start, opener, closer = min(starts)
            output.append(self.pending[:start])
            self.pending = self.pending[start:]
            end = self.pending.find(closer, len(opener))
            if end < 0:
                if final or len(self.pending) > 100:
                    self.pending = ""
                break
            source = self.sources.get(self.pending[len(opener):end])
            self.pending = self.pending[end + len(closer):]
            if source:
                emit_metadata("citation", {"id": source["id"], "label": source["label"]})
                output.append(f"[{source['label']}](#source-{source['id']})")
        return "".join(output)


def cited_answer(deltas: Iterator[str], chunks: list[dict]) -> Iterator[str]:
    parser = CitationMarkers(publish_sources(chunks))
    try:
        for delta in deltas:
            text = parser.feed(delta)
            if text:
                yield text
    finally:
        close = getattr(deltas, "close", None)
        if close:
            close()
    final = parser.feed("", final=True)
    if final:
        yield final
