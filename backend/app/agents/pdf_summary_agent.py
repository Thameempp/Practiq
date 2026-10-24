"""Sequential map/reduce over text supplied by the existing PDF pipeline."""

from app.agents.base import BaseAgent
from app.services.summary.chunks import prepare_chunks
from app.services.summary.models import SummaryChunk, SummaryConfig, SummaryError
from app.services.summary.prompts import EMPTY_CONTENT, summary_prompt
from app.services.summary.reducer import reduce_summaries
from app.services.summary.retry import call_with_retry
from dataclasses import replace
from app.services.summary.coverage import source_coverage
from app.services.summary.budget import can_finalize


class PDFSummaryAgent(BaseAgent[dict]):
    def __init__(
        self,
        generate_text,
        *,
        config: SummaryConfig | None = None,
        generate_final=None,
        on_progress=None,
        retry_generation=True,
    ):
        self.generate_text = generate_text
        self.generate_final = generate_final
        self.config = config or SummaryConfig()
        self.on_progress = on_progress or (lambda update: None)
        self.retry_generation = retry_generation


    def summarize(self, chunks, *, outline=None, request="") -> dict:
        return self.run(chunks, outline=outline, request=request)


    def _run(self, chunks, *, outline=None, request="") -> dict:
        chunks = list(chunks)
        prepared = prepare_chunks(chunks, self.config)
        direct = can_finalize(prepared, self.config, outline, request)
        coverage = source_coverage(chunks)
        notes = []
        self.on_progress({
            "label": f"Reading all {len(coverage['read_pages'])} PDF pages in {len(prepared)} passages…",
            "stage": "reading",
        })
        for index, chunk in enumerate(prepared, 1):
            prompt = summary_prompt(
                [chunk],
                final=direct,
                mapping=True,
                outline=outline if direct else None,
                request=request if direct else "",
                max_chars=(
                    self.config.max_summary_chars
                    if direct
                    else self.config.intermediate_chars
                ),
            )
            text = self._generate_final(prompt) if direct else self._generate(prompt)
            if text != EMPTY_CONTENT:
                notes.append(SummaryChunk(text, chunk.page_start, chunk.page_end))
            self.on_progress({
                "label": f"Saved passage {index}/{len(prepared)}; processed through PDF page {chunk.page_end}.",
                "stage": "reading",
            })
        if not notes:
            raise SummaryError("The PDF contains no substantive text to summarize.")
        self.on_progress({"label": "Combining the document summary…", "stage": "merging"})
        if not direct and len(notes) == 1:
            prompt = summary_prompt(
                notes,
                final=True,
                mapping=False,
                outline=outline,
                request=request,
                max_chars=self.config.max_summary_chars,
            )
            summary = self._generate_final(prompt)
        else:
            summary = reduce_summaries(
                notes,
                self._generate,
                self.config,
                outline=outline,
                request=request,
                generate_final=self._generate_final,
            )
        return {
            "summary": summary,
            "chunk_count": len(prepared),
            "coverage": coverage,
            "chunk_summaries": [
                {"summary": note.text, "page_start": note.page_start, "page_end": note.page_end}
                for note in notes
            ],
        }


    def _generate(self, prompt: str) -> str:
        if not self.retry_generation:
            return self.generate_text(prompt)
        return call_with_retry(
            self.generate_text,
            prompt,
            replace(self.config, max_summary_chars=self.config.intermediate_chars),
        )


    def _generate_final(self, prompt: str) -> str:
        return (
            self.generate_final(prompt)
            if self.generate_final
            else call_with_retry(self.generate_text, prompt, self.config)
        )
