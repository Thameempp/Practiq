# Shared topic hierarchy and evidence scope

Ingestion extracts the PDF outline before indexing, annotates the hierarchy, and
builds a versioned topic index. `services/topics/` stores structural data only:
parent IDs, title paths, page/word boundaries and existing chunk positions. The
index lives in SQLite `document_topics`, scoped by PDF and knowledge base.
The vector IDs, embeddings and Pinecone metadata remain unchanged.

`services/retrieval/topics.py` owns topic selection. Browser node IDs resolve to
the stored outline; client titles, excerpts, descendant lists and supplied paths
cannot override it. A parent includes its descendants. A selected subtopic ends
at the next sibling or enclosing boundary, including headings on the same page.
Missing, ambiguous or unanchored selections fail rather than widening to the PDF.
Heading matching preserves technical symbols such as C++.
Version 2 also matches exact chapter-heading lines whose number extracts after
the title, including fused forms such as `Operational ampliﬁers6`. Matching keeps
the actual source-word span so an immediately following subheading is not skipped.
Older local topic records rebuild automatically from the original PDF; vectors
and chunk positions do not need re-ingestion. Invalid quiz topic selections return
the actionable scope validation message instead of a generic service outage.

The Retrieval Agent applies these boundaries before fusion/reranking and to every
expanded neighbor. Dense search uses document identity and existing chunk-index
bounds; BM25 clips the corpus before scoring/top-k. Shared-page chunks are trimmed
to the actual selected text. When originals are available, indexed candidates use
the corresponding original words, avoiding stale text at known chunk positions.
Cross-encoder input includes canonical topic paths; those paths are structural
hints and are never added to quoted source text. General questions retain all-page
eligibility; inferred topic matches only guide search and ranking.

Dense filters combine range clauses using Pinecone's documented
[`$and` metadata operator](https://docs.pinecone.io/guides/search/filter-by-metadata).
They require no new vector fields or re-ingestion.

## Answer Verifier integration

The verifier selects disputed claims and judges whether supplied passages support
them. It does not choose topics, build search jobs, manage retrieval workers, or
duplicate ranking logic. `verification/search.py` delegates to
`retrieval/discovery.py`, which owns bounded evidence discovery and calls the same
topic-aware Retrieval Agent used by normal QA.

Verification scope resolves through retrieval's canonical topic service. Reused
citations must also lie inside that scope, so a valid citation from a sibling
topic is not automatically accepted. A citation spanning a sibling boundary is
discarded; discovery can return a narrower valid passage. Original-file/page/quote
confirmation and semantic verdict validation remain separate checks.

The review prompt, structured result, displayed topic path and audit entry carry
the canonical scope. Practice passes its selected topic through the explanation
and verification button. Chat keeps the original answer's scope when rechecking it.
Explicit scope belongs to one PDF; general cross-document checks remain available
with no selected topic.

## Lifecycle and limits

- Existing uploads with an original PDF and stored outline get a local index on
  first use, without provider calls or re-embedding. Matching indexes are reused.
- Hierarchy changes, source revisions or an index-version change rebuild the local
  index. Cached cleaned pages/words are bounded to four PDFs.
- Deleting a PDF removes its topic index alongside existing conversation/citation
  cleanup. Internal positions are not returned by the public document-list API.
- Selection follows extracted headings and text. Scanned pages need OCR; absent
  or ambiguous heading anchors cannot establish a reliable explicit scope.
- Retrieval remains bounded evidence discovery. Topic membership alone never
  establishes that a claim is true; that decision belongs to the verifier.
