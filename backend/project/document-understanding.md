# Document Understanding Agent

The project previously had outline extraction and a shared topic index, but no
dedicated document-understanding agent or page inventory. The agent now runs during
ingestion before embeddings, reusing those existing components.

## What it builds

- Metadata: physical page count, filename, PDF title/author, declared language.
- Every physical page: dimensions, rotation, text availability, printed label and
  its source, raster/vector counts, probable table/equation/caption regions.
- Sections: parent/child relationships, actual page ranges, special-section roles,
  confirmed/probable/uncertain status, source excerpts, and rule-based confidence.
- Heading topics and definition candidates: parent chapter/section and existing
  chunk IDs. These remain separate records from structural sections.
- Quality issues: scanned/unreadable/blank candidates, extraction failures,
  repeated-content candidates, and outline/page mismatches.

Printed contents pages and subject indexes are separate kinds; embedded PDF
bookmarks are recorded separately again. Numbered chapters titled Introduction
retain their chapter type and introduction role. Chapter labels inside an answer
appendix do not inflate the main chapter count.

## Validation and lifecycle

`DocumentUnderstandingAgent` delegates page inspection, structure reconciliation,
section construction and topic mapping to small modules in `services/understanding/`.
Unmatched headings receive an exact, bounded nearby-page recheck. Contents-page
entries cannot confirm the location of the actual chapter. A PDF without a usable
outline gets conservative heading-pattern candidates. Unresolved boundaries remain
uncertain and explicit retrieval scope continues to fail closed.

The agent returns a map and the reconciled hierarchy/topic index. The service saves
the same index used by Retrieval, MCQ generation and the Answer Verifier, so none
of those agents duplicate topic selection. Existing full-PDF summary coverage stays
in the summary pipeline; selected-chapter summaries use the reconciled hierarchy.

SQLite tables `document_maps`, `document_map_pages`, `document_map_sections`, and
`document_map_topics` keep maps separate from chunks. Section parents are explicit
relational fields. This uses the project's existing database rather than introducing
PostgreSQL solely for the new feature. Original-file revision, map version, topic
version and hierarchy signature govern cache reuse. Existing uploads backfill on
map access; file changes trigger rebuilding. Deletion purges all map rows, and an
in-flight analysis cannot restore rows for a deleted document.

No Pinecone IDs, metadata, embedding model, or chunk text change. Re-uploading
unchanged PDFs is unnecessary.

## API and chat

- `GET /documents/{document_id}/map?knowledge_base_id=local` returns the map.
- Add `&refresh=true` to explicitly re-examine a partial map.
- Membership, document readiness and original-file access are checked before access.
- `/ask` routes page/chapter counts, chapter topic lists, detected special-section
  locations and topic-to-chapter queries directly to structural records. No LLM or
  vector retrieval is needed for those requests. Matching locations are clickable
  physical-PDF page citations. General semantic questions keep the existing RAG path.
- The existing outline receives page ranges, printed labels and detection status;
  these appear in node tooltips without replacing the navigator.

Examples: "How many pages does this PDF have?", "How many chapters are there?",
"List all topics in Chapter 2", "Where is the conclusion?", "Does this PDF have an
appendix?", "Which chapter discusses resonance?".

## Limits

This implementation uses deterministic inspection and bounded local rechecks.
It does not call an LLM to reinterpret ambiguous layouts. Confidence values are
heuristic, not calibrated probabilities. Definition/visual/table matches are
candidates; the agent does not perform OCR, semantic diagram interpretation, or
claim to recover content missed by extraction. Missing physical pages cannot be
proved from a PDF alone. "Not detected" does not mean "does not exist".

The APIs follow the existing local knowledge-base access model, not a new account
authentication system. Inspection uses the documented [PyMuPDF page APIs](https://pymupdf.readthedocs.io/en/latest/page.html)
and [document metadata/page-label APIs](https://pymupdf.readthedocs.io/en/latest/document.html).
