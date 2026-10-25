# Answer Verifier

`app/agents/answer_verifier_agent.py` coordinates on-demand verification. Small
modules in `app/services/verification/` own detection, schemas, PDF confirmation,
budgets, discovery delegation, review validation, rendering and bounded storage.
Topic selection and evidence discovery are owned by `services/retrieval/`, using
the topic index built during ingestion. See `topic-aware-retrieval.md`.

## Using it

In an existing chat, send “Are you sure?”, “Check again”, “I think you're wrong”,
or “Please verify the explanation”. Keep the same `conversation_id`. `/ask`
resolves the last completed answer and its original question, scope and source
IDs. Missing answers, removed PDFs or a different selected section ask for a
valid target rather than verifying an unrelated answer. Older retained chats are
usable, with an explicit partial-answer limitation. Refusals update the latest
verification target without entering factual conversation history.

The practice explanation includes **Verify answer and explanation**. It sends the
generated correct option, all option texts, explanation and canonical source IDs.
It also carries the selected topic scope; sibling-topic citations are excluded.
Verification does not silently change the quiz score or overwrite its answer key.

Explicit callers can use `POST /verify` with this shape:

```json
{
  "knowledge_base_id": "local",
  "conversation_id": "optional-chat-id",
  "target": {
    "question": "What input does binary search require?",
    "answer": "Binary search requires a sorted input.",
    "document_ids": ["uploaded-document-id"],
    "source_ids": ["canonical-source-id"],
    "artifact": "answer",
    "objection": "Check the input requirement."
  }
}
```

`artifact` accepts `answer`, `summary`, or `mcq`. Source IDs are optional; without
reusable passages, the verifier performs bounded targeted retrieval. Ordinary JSON
returns the structured result plus rendered `content`. With `Accept:
text/event-stream`, it uses the existing progress, sources, citation, text, error
and done events, plus a `verification` event containing the structured result.

## Evidence and verdicts

The agent extracts up to eight verbatim factual claims, reviews each separately,
and returns `supported`, `contradicted`, `partially_supported`,
`insufficient_evidence`, or `conflicting_sources`. Claim IDs must match exactly;
unknown IDs, missing claims, fabricated quotes, wrong proof roles and unsupported
corrections fail closed. Opposing proof from different PDFs stays a conflict.

Python confirms current KB membership, readiness, original-file revision, physical
page and quote text. Source IDs alone do not establish factual support. Range-only
summary links cannot prove a specific claim. Verified subquotes get canonical
source IDs opening the exact passage on the original PDF page.

The original question, answer and objection remain separate prompt data. PDF text
and prior responses are never instructions. Normal QA/summary/quiz requests incur
no additional verifier model calls. A caller can also invoke the agent/service
from a separate quality-control rule.

## Limits and lifecycle

- Up to three bounded model calls: extraction, initial review, optional re-review.
- One additional retrieval round, at most four searches, two concurrent workers.
  Retrieval owns these workers and topic filtering; the verifier only judges claims.
- Original answer capped at 4,000 counted tokens; omitted claims, truncated answers
  and budget-excluded sources are explicitly marked as incomplete coverage.
- Full prompts reserve the existing chat output/framing budget. SDK retries are
  disabled; cancellation and remaining task deadlines carry into search workers.
- Latest targets and the last ten audit entries use existing expiring SQLite
  conversation state. Audit entries link initial/final verdicts, evidence IDs,
  correction reasons and original response ID. PDF deletion purges related state.
- Grounded corrections enter follow-up memory under the original topic. Repeated
  doubt continues to reference the original answer, preserving audit lineage.
- Semantic support, arithmetic interpretation and units are model-reviewed;
  there is no symbolic calculation engine or calibrated confidence percentage.
  Summary claim checks do not prove exhaustive coverage or every possible omission.
  Missing/scanned original text, provider errors and invalid reviews yield uncertainty.
