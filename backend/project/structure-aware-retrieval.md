# Document understanding connected to retrieval

`retrieve_evidence` now calls `resolve_retrieval_context` before hybrid search.
The adapter consults the Document Understanding Agent's saved map through the
existing revision/version/signature-checked service. Warm requests reuse the map;
missing or stale maps are built/refreshed from the original PDF locally.

## Evidence flow

1. Resolve the registered document and its own knowledge base, load its map, then
   resolve the canonical topic index. This order prevents stale topic boundaries
   after map refresh.
2. Match detected headings/definitions and confirmed chapter/unit/part references.
   Parent paths expand the search query. Bare chapter headings inside an answer
   appendix cannot override the confirmed main chapter.
3. Dense search and BM25 retain their normal document and explicit-topic filters.
   Inferred map topics are soft hints: every page remains eligible globally.
4. Add at most eight map-linked original passages, within the existing candidate
   cap. Sample long sections across their full chunk range and interleave matches.
   Map excerpts are never inserted as evidence; only original chunk IDs/text are
   accepted. Canonical scope clipping applies to these passages and neighbors.
5. Rerank all candidates against the original question and apply the existing
   shared token budget. Document structure, detection confidence, printed page
   labels and extraction warnings are separate annotations, counted in the budget.

The Answer Verifier and MCQ workflows already use this retrieval service and
therefore benefit from the connection without duplicating evidence discovery.
The verifier still decides whether original evidence supports a claim.

## Focused modules

- `retrieval/understanding.py`: cached-map consultation and query/topic matching.
- `retrieval/structure_context.py`: scope-safe annotations and original-PDF seeds.
- `retrieval/structure_evidence.py`: bounded candidate merge and structural labels.
- `agents/retrieval_agent.py`: combines candidates before reranking.

Stats expose `understanding_map`, `structure_candidates` and
`latency_ms.understanding`. No additional provider/model calls or vector schema
changes are introduced. Missing originals retain the existing indexed-evidence
fallback, without claiming that a document map was available.

## Validation (2026-10-24)

- Fourteen new tests cover chapter references, definitions, exact source text,
  explicit scopes, all-page eligibility, cache reuse/refresh, document isolation,
  uncertainty, scanned-page warnings, candidate/token caps and reranking rejection.
- Local 269-page electronics PDF: the old topic matcher chose
  `Appendix A: Selected answers to exercises > Chapter 6`; map consultation chose
  `6 Operational amplifiers`. Discovered original passages span physical pages
  169, 171, 173, 176, 179, 181, 183 and 187. Global scope stayed unrestricted.
- Observed local map lookup: 33.19 ms first, 18.06 ms warm; seed discovery: 48.97 ms.
  These are one-run measurements, not service latency guarantees.
- Full backend suite: 350/352 pass; two existing missing hierarchy PDF fixtures.
- Live semantic answer-quality evaluation was not run; no provider quota used.
