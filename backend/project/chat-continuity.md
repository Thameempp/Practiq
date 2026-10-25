Conversation continuity and token management

`conversation_id` now identifies bounded server-side turns as well as PDF selection
and pending clarification state. The browser sends the current question and chat ID;
it does not resend the entire transcript or provide trusted historical answers.

Flow

1. Resolve document membership, readiness, names and section scope normally.
2. Recognized follow-ups reuse explicitly selected documents/groups when no different
   PDF or section was selected. General QA searches all current uploads, including
   PDFs added since the previous turn. Generic “Summarize” still requires a
   document choice when multiple PDFs exist.
3. `chat/context.py` loads consecutive turns matching the document set and section
   hash. Knowledge-base-wide turns also retain their topic when the current set
   grows, while fresh retrieval searches the expanded set. Explicit document/section
   switches and removed documents start a fresh contextual segment. Turns record
   `knowledge_base_wide` so follow-ups do not freeze the upload set. Legacy turns
   without that field do not implicitly restrict general QA to the old active PDF.
4. `chat/followup.py` adds the previous topic and a small previous-answer excerpt
   to referential search queries. “deep heading hierarchy” followed by “list the four
   levels” therefore retrieves with both concepts. The topic anchor survives chains
   of follow-ups. A new explicit topic replaces it. Search expansion is deterministic
   and bounded to 2,000 counted tokens; it makes no additional model call.
5. Fresh PDF evidence is retrieved on every request. `chat/budget.py` fits the system
   instructions, current question, scope, complete user/assistant history pairs,
   PDF passages and message framing into one input allowance. The current question
   is kept intact in generation. Over-budget required input fails with a clear message.
6. `chat/llm.py` sends the bounded role-based history and current evidence with an
   explicit output cap. Prior answers identify conversational references; they are
   not factual evidence. The model must ground claims and page citations in the new
   passages, and ask for clarification when a reference remains ambiguous.
7. Only fully successful, evidence-backed workflows are saved after execution.
   Cancelled, failed, timed-out, partial and evidence-free answers are not added.
   Output-limit truncation fails visibly instead of creating a completed history turn.

Default budgets (configurable in `.env.example`)

| Setting | Default | Purpose |
| --- | ---: | --- |
| `CHAT_CONTEXT_TOKENS` | 16,000 | Application budget for input plus reserved output/framing |
| `CHAT_OUTPUT_TOKENS` | 2,048 | Maximum provider completion tokens, including model reasoning |
| `CHAT_SAFETY_TOKENS` | 256 | Additional template/framing margin |
| `CHAT_HISTORY_TOKENS` | 2,400 | Maximum historical messages in a QA prompt |
| `CHAT_MEMORY_TOKENS` | 10,000 | Maximum retained serialized transcript budget |
| `CHAT_MAX_TURNS` | 12 | Maximum retained exchanges before dropping oldest turns |
| `CHAT_TTL_SECONDS` | 86,400 | Memory expiration after inactivity |

Example input allowance: 16,000 − 2,048 − 256 = 13,696 counted tokens. History has
its own cap inside that allowance. At least one evidence passage is reserved before
history is selected; supplementary evidence is added only while the complete prompt
fits. Cross-PDF answers additionally require every document with retrieved evidence
to remain represented. Explicit comparisons require evidence from every requested
PDF. An oversized latest historical turn can be shortened as a complete
user/assistant pair; older pairs are dropped whole. Stored questions, answers and
topic anchors have individual caps as well as the total retention budget.

Counting reuses `services/retrieval/tokens.py`: a configured local generation
tokenizer is preferred; otherwise UTF-8 byte length is a conservative offline
estimate. The application budget is not a claim about the model's maximum context
window. Configure limits for the deployed model and reasoning/output needs. Logs
contain token estimates, counter method and counts, without conversation/PDF text.

Persistence and lifecycle

- SQLite uses the existing `conversation_state` table with kind `history`, scoped
  by knowledge base and chat ID. Atomic read/modify/write prevents lost concurrent
  appends; request IDs deduplicate repeated completion records. Turns are ordered
  by request preparation time. Concurrent requests use independent history snapshots.
- Deleting a PDF purges turns that reference it, including group comparisons.
- The browser saves the same chat ID and up to 40 complete message records/60,000
  characters in tab-local session storage for refresh continuity. Pending empty
  replies are omitted. This display history is never sent as trusted model history.
- “New chat” stops streaming, rotates the ID, clears messages and section focus.
  Clearing the knowledge base also rotates the ID. Old server memory expires.
- Memory is intentionally finite. Very old references outside retained context may
  need the user to name the topic again. Follow-up detection is a bounded heuristic,
  not an extra model-based query rewrite.
- Exchanges completed before this feature was installed have no server transcript;
  memory starts with successfully completed exchanges after the change.

Tests cover the pictured follow-up through `/ask` with mocked provider streams,
history roles and retrieval expansion, complete prompt/output budgeting, Unicode and
JSON escaping, namespace/section isolation, atomic append/idempotency, expiry, PDF
deletion, failed/cancelled answers, browser restoration and a fresh chat ID.
