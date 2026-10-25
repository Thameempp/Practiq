Large-PDF summary failure — 2026-10-23

Reproduction and cause

- The uploaded textbook contains 269 pages and produces 923 source chunks.
- The old character-only packing created 26 passages up to 20,000 characters and
  allowed another 2,400 completion tokens per request.
- A live diagnostic using generated hash strings (no PDF/chat content) received
  Groq HTTP 413: the model's account quota was 8,000 tokens/minute and the generated
  20,689-byte request required 11,458 tokens. The old size guard did not prevent it.
- A fixed ten-minute task deadline also cannot accommodate a long quota-limited
  textbook job. Completed stages previously had to be regenerated after a failure.

Changes

- `summary/budget.py` counts instructions and prompts before requests, reserves
  completion capacity, and packs source text under the token allowance.
- Defaults: 5,500 counted input tokens + 2,048 completion tokens, below the observed
  8,000 allowance. The existing configured local tokenizer is used when available;
  UTF-8 byte counts provide a conservative offline fallback.
- Intermediate summaries are limited to 1,200 characters; reduction and optional
  cross-PDF consolidation also obey the token budget. All source text is processed.
- Successful intermediate/final responses are checkpointed in SQLite for seven days.
  Retrying an identical request reuses successful stages. Partial streams never
  become cached completed summaries. Checkpoints disappear when their PDF is deleted.
- Retry-After waits can reach 120 seconds. Safe provider messages replace generic
  failures. Final streams can retry before text is visible, and never replay text
  already published. The SDK does not add its own nested retries.
- Large-document deadlines scale by chunk count, with a configurable two-hour cap.
  This allows quota waits; it does not guarantee a two-hour completion time.
- The browser requests SSE progress/text/error/completion events. Reading-page and
  quota-wait status stays separate from prose. Ten-second keep-alive comments keep
  silent waits active. Older plain-text clients continue to work.

Validation

- The same generated 20,689-byte fixture becomes five safe passages; the first
  bounded provider call completed successfully (5,196 counted input upper bound,
  2,048 reserved completion tokens).
- Local validation on the actual uploaded file preserved every source word across
  all 269 pages and 923 chunks. It produced 137 bounded passages and 183 mocked
  map/reduce stages; the largest input upper bound was 5,227 tokens. Page 269 remained
  in the coverage. No PDF content was sent to a model during this local check.
- Tests cover cache resume/invalidation, request/output limits, quota handling,
  progress separation, fragmented UTF-8 SSE, cancellation and interrupted streams.

The live diagnostic containing PDF text was rejected by automatic approval review.
Full live-model validation on the PDF requires explicit authorization to send that
text to the configured Groq API. Generated-fixture diagnostics were permitted.

Provider references: https://console.groq.com/docs/rate-limits and
https://console.groq.com/docs/reasoning.
