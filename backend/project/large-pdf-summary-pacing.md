# Large-PDF summarization with bounded provider work

The summary service reads the original PDF, not retrieved top-k passages. It scans
all text pages and records empty pages separately. No page-count cutoff is used.

## Processing strategy

1. Small documents keep full text. For 80+ readable pages, local term-frequency /
   inverse-document-frequency scoring selects diverse informative excerpts from
   **each** page, with boosts for definitions, results, limitations and formulas.
   Selection examines the entire page rather than choosing its opening sentences.
   This is extractive compression, not semantic understanding of every detail.
2. Pack the selected material in PDF order into conservative token-bounded map
   requests. Every text page participates; there is no first-pages-only sample.
3. Generate compact passage notes, validate/repair them before checkpoint storage,
   and merge bounded groups hierarchically. Only the final presentation uses the
   user's requested summary format/focus. Saved notes are reusable across requests.
4. Stream the final overview after all passage notes are available. Intermediate
   notes remain internal; progress reports completed passages/pages and quota waits.

The response discloses whether all-page excerpts were used. The result's coverage
includes strategy, original/selected character counts, read pages and textless pages.
All source text contributes to a revision fingerprint so edits to even unselected
text invalidate the cached result. Successful checkpoints remain resumable for
seven days; partial/invalid outputs never become completed checkpoints.

## Provider controls

- Shared rolling per-minute request/token reservations cover map, merge and final
  requests using the same provider client/model in this process. Actual usage
  refunds unused output reserve, including Groq's streamed `x_groq.usage` form.
- Requests wait before sending when the configured budget is full. Waiting is
  cancellable; output reserve counts toward the request budget.
- SDK automatic retries remain disabled. One bounded retry owner handles each
  stage and honors Retry-After. Oversized drafts are compacted whole when they fit
  the repair input budget rather than blindly repeating the same source request.
- GPT-OSS uses low reasoning effort and excludes reasoning from visible content.
  The existing model remains the default; SUMMARY_MODEL can select another model
  available to the account without altering retrieval embeddings or vector IDs.
- Long summary tasks receive the configured overall summary deadline rather than
  a short per-page timeout that ignores provider pacing.

Set these in backend configuration, matching actual account/model limits:

| Setting | Default |
| --- | --- |
| SUMMARY_REQUESTS_PER_MINUTE | 20 |
| SUMMARY_TOKENS_PER_MINUTE | 8000 |
| SUMMARY_INPUT_TOKENS / SUMMARY_OUTPUT_TOKENS | 5500 / 2048 |
| SUMMARY_MODEL | existing LLM_MODEL |
| SUMMARY_DIGEST_THRESHOLD_PAGES | 80 |
| SUMMARY_PAGE_DIGEST_CHARS | 900 |
| SUMMARY_MAX_TIMEOUT_SECONDS | 7200 |

Input budgets automatically fit the configured token rate minus output reserve.
The configured local budget cannot bypass daily quotas, other clients/agents using
the same account, or separate server processes. External throttling still uses
bounded retry/checkpoint recovery. Image-only pages require OCR before meaningful
summarization; this change does not implement OCR or diagram interpretation.

## Verification

Fourteen tests cover 500-page coverage, late chapter preservation, whole-draft
repair, cross-format cache reuse, all-page excerpt selection, revision invalidation,
quota waiting/refunds/cancellation and the real installed Groq SDK against a mocked
HTTP transport. No live provider quota was consumed.

The generated 500-page PDF contained 1,252,942 extracted characters. Local excerpts
used 78,442 characters, reducing planned map requests from 500 to 21; the simulated
map/reduce used 29 total calls and preserved all 500 page / 10 chapter markers.
This repeated-background fixture demonstrates coverage and call reduction, not
live semantic accuracy or a universal compression ratio. The actual current
21-page PDF retained all 20,789 characters (7 planned map requests before/after).

Provider behavior follows [Groq rate-limit documentation](https://console.groq.com/docs/rate-limits)
and [reasoning/output controls](https://console.groq.com/docs/reasoning).
