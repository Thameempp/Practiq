# Rolling practice

Practice starts with five questions. Answering any previously unanswered question creates one refill credit: answering Q1 requests Q6, answering Q2 requests Q7. Only one refill request runs at a time. The learner keeps using the loaded questions while replacements arrive; revisiting an answered question does not request another replacement.

## Frontend

- `usePracticeQueue` binds the session to a document/topic, restores saved progress and aborts obsolete fetches.
- `practiceQueue` maintains five unanswered questions, consumes answer credits sequentially and ignores late results after disposal.
- `practiceState` rejects duplicate stems and keeps IDs distinct without overwriting answers.
- `practiceStorage` saves questions, answers and navigation per document/topic. Old five-question caches become exclusion history rather than repeated practice questions.
- `practiceApi` sends count=1 for refills and at most 100 exclusion stems. Network/429/503 retries are bounded to three attempts, respect bounded Retry-After waits and observe cancellation. Duplicate exhaustion is not automatically retried.
- The existing practice view keeps five navigation pills near the active question, preserves Prev/Next and source explanations, and reports correct answers / answered questions. Regenerate and the fixed-batch completion banner are removed.

## Backend

`POST /mcq` retains its existing contract and accepts optional `exclude_questions` (up to 100 strings, each 1–1000 characters). Orchestration verifies document ownership, readiness and scope before requesting fresh questions.

`services/mcq/practice.py` wraps the existing generation/evaluation pipeline. `history.py` persists question stems by document/topic in SQLite `practice_questions`. Successful generation receives UUID question IDs. Deleting the PDF purges its practice history; history cannot be committed for an already-deleted document.

`novelty.py` checks case/Unicode/punctuation-normalized text and close rewordings against all saved stems and within each new batch. Model context contains at most 4,000 characters of recent question history. The existing answer-review call also requires a positive semantic `distinct` verdict when previous questions exist; missing/negative novelty verdicts fail closed. Source grounding, exact quotes and answer validation remain mandatory.

History is committed under an immediate SQLite transaction with a second duplicate check, so concurrent requests cannot publish the same question. Repeated candidates get at most one additional generation attempt. If no distinct supported question passes, practice pauses while retaining loaded questions. Finite source material cannot guarantee unlimited distinct questions; model judgments about semantic novelty remain fallible.

The history table is created automatically by the existing database initializer. No vector schema, embedding model or PDF re-ingestion changes are required.

## Validation

Offline tests cover serialized Q6/Q7 refill, duplicate clicks, resume, disposal, duplicate rejection, request bounds, quota-wait cancellation, persistent topic isolation, concurrent saves, deletion cleanup and the API path through generation/review. No live model/provider requests were made.
