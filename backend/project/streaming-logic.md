Progressive response rendering

`/ask` keeps its existing text-stream and clarification-JSON contracts. Clients can
also request `Accept: text/event-stream` for progress/text/error/completion events.
The frontend uses this opt-in format; page progress and quota waits are rendered
independently of prose. Ten-second keep-alive comments cover silent processing.
Response
headers already disable caching and nginx buffering. QA forwards provider deltas
immediately; the former 40 ms sleep per delta has been removed.

PDF summaries retain full source coverage and sequential map/reduce. Intermediate
notes use the existing bounded retry policy. The single-passage summary, final
document reduction and final cross-document consolidation use
`services/summary/streaming.py`. It publishes actual provider text, validates size
and truncation, suppresses the boilerplate marker, checks cancellation and closes
the provider stream. A final request may retry before publishing text; it is never
replayed after any text is visible. Complete stages are checkpointed for resumption.
Task failures remain visible and cannot become successful partial summaries.

Frontend flow:

1. `streamRequest.js` handles fetch, API errors and clarification JSON.
2. `readTextStream.js` decodes UTF-8 incrementally and cancels pending reads on abort.
3. `streamStore.js` publishes the first text immediately, then batches updates over
   35 ms. Completion and Stop flush the remaining text immediately. Reset/disposal
   clear old timers and pending content.
4. `useTextStream.js` owns request identity, cancellation, completion and errors.
   It updates React parent state only at request boundaries, not for each token.
   Replaced or unmounted requests cannot update the current reply.
5. `StreamingReply.jsx` subscribes to the active response with `useSyncExternalStore`.
   `App.jsx` adds messages with stable UUIDs and saves the final/partial reply to
   conversation state once it settles. Completed messages retain their content.
6. `markdownBlocks.js` scans newly received lines and keeps completed blocks stable.
   It holds open fences, loose lists, tables and display math until safe boundaries.
   `StreamingMessage.jsx` memoizes completed Markdown blocks and renders the
   unfinished tail as lightweight text. Completion runs the existing full
   react-markdown/GFM renderer once so document-wide Markdown references resolve.
7. Active-response layout updates follow the existing scroll position policy.
   Scrolling upward pauses automatic following; the latest-response button resumes
   it. Per-token animations and conversation-wide Markdown parsing are avoided.

No additional runtime dependencies, syntax-highlighting/math libraries or message
virtualization were added. Long conversations are not virtualized without profiling
evidence. MCQs retain their existing complete validation/review before publication.

Verification uses mocked provider streams and native Node tests for burst batching,
immediate final flush, UTF-8 splits, cancellation, late responses, partial failures,
stable Markdown blocks and progressive final summaries. The burst test delivers
100 updates and observes one initial notification plus one scheduled batch.
Frontend lint and production build pass. Browser frame-rate and real-provider
latency have not been benchmarked. Streaming removes application delays; retrieval,
provider inference and long-summary preparation still take time before first prose.
