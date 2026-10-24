Agents share `BaseAgent.run(...)`, which checks task cancellation/deadlines before
work and before returning a result. The existing named methods remain available.
Providers are injected; importing these classes does not create provider clients.

| Agent | Named method | Result |
| --- | --- | --- |
| `RetrievalAgent` | `retrieve(question, document_id, search_query=...)` | Evidence, context, counts and timings |
| `PDFSummaryAgent` | `summarize(chunks, outline=..., request=...)` | Summary and chunk/page coverage |
| `MCQGenerationAgent` | `generate(document_id, scope=..., count=5)` | Validated `MCQResponse` |
| `EvaluationAgent` | `evaluate(raw_content, passages, document_id=..., count=...)` | Validated `MCQResponse` or an exception |
| `AnswerVerifierAgent` | `verify(target)` | Claim verdicts, grounded corrections, precise PDF sources and coverage limits |
| `DocumentUnderstandingAgent` | `understand(document, pages=...)` | Full-PDF structural map, reconciled hierarchy and shared topic boundaries |

Retrieval stays document-scoped and source-addressable. Summary uses all supplied
chunks in sequential map/reduce. Their existing service adapters remain in
`services/retrieval/service.py` and `services/summary/service.py`.
For `/ask`, the summary service injects `generate_final` so final prose streams
through the task context. Intermediate maps and merges remain internal; final
stream failures are reported without replaying text already shown to the user.

MCQ generation retrieves bounded evidence, generates JSON, then invokes evaluation.
Evaluation validates question structure, distinct options/questions, expected count,
document identity, unique source IDs and exact quotes. Filenames and physical PDF
pages come from stored metadata, never model-authored page numbers.

A separate model call reviews whether the correct answer and every explanation
claim follow from the cited quotes, and whether the question is unambiguous. Every
question must have a complete affirmative verdict. Missing/malformed/negative
verdicts reject the quiz; no partial quiz is returned. This is a model quality check,
not a mathematical guarantee of correctness or a check against outside sources.

`generate_text(system_prompt, prompt) -> str` is shared by generation and evaluation.
Production calls use `services/mcq/llm.py`; tests can inject a deterministic callable.
`services/mcq/generator.py` preserves `generate_mcqs` and `MCQGenerationError` for
the existing `/mcq` orchestration workflow. A successful quiz now needs two model
calls, one for generation and one for review, within the existing task deadline.

The coordinator owns document readiness, knowledge-base membership, task execution
and error reporting. Agents do not resolve ambiguous documents or select namespaces.
Supporting prompts, schemas, evidence validation and provider code live in focused
service modules. Study-material requests remain outside these implemented workflows.

QA continuity is owned by `app/chat/`, keeping transcript storage and complete-prompt
budgets separate from agents. Retrieval receives a bounded contextual search query;
generation receives recent role-based turns plus freshly retrieved PDF evidence.
Details: `backend/project/chat-continuity.md`.

Answer verification is selective: doubt requests in `/ask` and explicit `/verify`
requests reuse original evidence before one bounded targeted-search round. It is
separate from mandatory MCQ generation evaluation. Claims, quotes, document access
and verdict/proof consistency are validated; semantic judgments remain model based.
Details: `backend/project/answer-verifier.md`.

Topic trees are indexed during ingestion. Retrieval owns canonical topic selection,
descendant boundaries, filtered dense/BM25/neighbor evidence and shared discovery.
The Answer Verifier delegates to it and judges support; it does not implement topic
selection or independent search logic. See `backend/project/topic-aware-retrieval.md`.

Document Understanding runs before vector ingestion. It inventories every physical
page, checks outline locations, separates printed labels from physical pages, and
persists page/section/topic records in the existing SQLite store. `/documents/{id}/map`
and structural `/ask` requests reuse that map. Scans, visual candidates, duplicates,
and uncertain headings are reported rather than interpreted as proven facts.
See `backend/project/document-understanding.md` for scope and limitations.
