Service cleanup — 2026-10-23

The audit followed Python imports transitively from `backend/main.py` and the
FastAPI application, then checked repository callers, tests, patch targets,
dynamic-import usage and notebook code. The notebook is empty; no dynamic service
loader is present. Eight Python service modules had no application callers:

| Removed module | Current implementation |
| --- | --- |
| `services/bm25.py` | `services/retrieval/sparse.py` owns BM25 retrieval |
| `services/retriever.py` | `services/retrieval/service.py` and `RetrievalAgent` |
| `services/vector_search.py` | `services/retrieval/dense.py`, `ranking.py`, and the agent |
| `services/cleaner.py` | PDF extraction handles text in `loader.py` and `page_noise.py`; the NLTK cleaner was never called |
| `services/document_summary.py` | `services/summary/storage.py` reads all persisted chunks |
| `services/summary_sampler.py` | `PDFSummaryAgent` summarizes every chunk using sequential map/reduce |
| `services/content_filter.py` | Summary preparation preserves source text; the summary prompt handles boilerplate |
| `services/summary_intent.py` | `query/analyzer.py` owns intent classification |

`services/working.txt` was an outdated pipeline sketch with no code callers;
the current pipeline descriptions remain in the other `project/*-logic.txt` files.

`test_content_filter.py` and `test_summary.py` exercised the removed filter,
sampler and intent wrapper. Their obsolete implementation tests were retired.
Outline request validation moved to `test_document_scoping.py`; the summary/QA
intent examples are covered directly in `test_query_analyzer.py`. Current summary
coverage, page preservation, storage and map/reduce tests remain in place.

Active compatibility modules such as `hierarchy_extractor.py` are retained because
the upload pipeline imports them. Package initializers and files with any active
callers are retained. This cleanup does not change provider configuration, stored
PDF data, dependencies or API behavior.

Validation: all 55 remaining service modules are reachable through application
imports, and no backend/test import or patch target references a deleted module.
Before cleanup, the suite ran 191 tests with four errors (two obsolete `src`
patch targets and two missing PDF fixtures). After cleanup, it ran 180 tests:
178 passed; the same two hierarchy tests still need their sample PDFs.

Copies of the nine removed service files and two retired test files were saved
before deletion at `/tmp/practiq-service-cleanup-ecevno8b/backend/`.
