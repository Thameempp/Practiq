# Full-document summaries and retrieval

## Problems corrected

An active outline section could narrow “summary of this PDF” to the first chapter. “All pages of this PDF” could also be interpreted as every document in the knowledge base. Long outline metadata could erase the user's focus and show only early headings. Summary storage trusted the indexed chunk list without checking completeness, while BM25 trusted any nonempty memory cache. Closely overlapping early passages could then occupy the final evidence budget.

## Summary flow

`summary/storage.py` now prefers all physical pages of the registered original PDF, read by `services/pdf_source.py`. It preserves full page text for map/reduce; it does not summarize a search result or use retrieval's top-k limit. This also avoids repeating the overlapping text in retrieval chunks. Extraction uses a bounded four-file cache keyed by path and file revision, with cancellation checks while reading pages and before returning cached content.

When the original is unavailable, the indexed fallback must contain exactly the registered chunk IDs. A known document with unknown/zero chunk count cannot establish completeness. Missing chunks cause a clear error rather than a successful prefix-only summary. Unregistered legacy helper calls retain their old behavior; public requests must first resolve a registered document through orchestration.

Explicit whole-document requests override an active section's page range while retaining its document selection. Explicit chapter/section summaries continue to use their selected range. The query parser distinguishes all pages of one PDF from all PDFs.

The metadata builder reserves space for the user focus separately and distributes bounded outline hints across the outline. Multi-part map prompts rely on their actual source text rather than the opening outline. Reduction instructions require coverage across all input summaries, including later chapters and conclusions. Checkpoint version 2 invalidates previously generated summaries under the old prompts.

Each result carries `coverage.read_pages` and `coverage.pages_without_text`. The response reports how many pages with selectable text were processed and identifies pages without text. Blank/scanned pages are inspected but their image content is not summarized. OCR remains outside this change. Map/reduce still compresses facts; reading every page does not guarantee the model will mention every detail.

## Retrieval and reranking

The lexical corpus and neighbor expansion prefer the full original PDF. They reuse the same page cleaning, chunking, IDs and metadata as ingestion. No vectors, Pinecone metadata, model settings or namespaces are migrated. If no original is available, a partial memory cache is completed from persisted chunks and checked against the registry.

BM25 removes common conversational filler while retaining negation and quantities. Exact score ties are distributed across the document before the candidate cutoff, so equally ranked later pages can reach the cross-encoder. Stronger lexical scores remain ahead of weaker ones.

The cross-encoder must return one finite score per input candidate; short/nonfinite results fail instead of silently dropping the tail. Final selection uses relevance plus a small overlap penalty (`RetrievalConfig.diversity_weight=0.15`) to reduce redundant context. The top-ranked first passage stays first, token limits still include headers, and exact duplicate text is still excluded. Cross-document comparison retains its existing document-first allocation with diversity disabled at that shared selection step.

QA searches across the complete document and reranks a bounded candidate pool. Full summaries process all available source pages sequentially, independently of those retrieval limits.

## Verification

- Before changes, the targeted regression set reproduced 11 failing assertions/subtests covering original-file coverage, incomplete indexes, partial caches, whole-document routing, outline truncation, duplicate context and incomplete reranker scores.
- `cd backend && .venv/bin/python -m unittest discover -s tests -t .`: 253 tests run, 251 passed. The same two hierarchy tests lack their PDF fixtures (`computer_science_sample.pdf`, `Python_Smaller_Concepts_for_NLP_Practicals.pdf`).
- `cd frontend && npm test`: all 33 tests passed.
- A generated 269-page PDF preserves all 269 page markers through final map/reduce under the configured input budget. Full-source hybrid retrieval puts a fact found only on page 269 first, despite dense candidates coming from the opening pages. Model generation/scoring is deterministic in this regression; it is not a live LLM quality evaluation.
- Separate regressions cover partial indexed fallbacks, blank later pages, original-file neighbor expansion, score-tie page distribution, and unchanged explicit chapter scoping.
- No uploaded PDF was sent to an external model, and no vector re-ingestion is required. Actual live model prose quality remains unverified in this run.
