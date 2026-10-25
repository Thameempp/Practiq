# Clickable PDF citations

New QA and cross-document answers cite backend-owned source IDs. Clicking a reference opens the original PDF in a modal on the physical, 1-based cited page. Quiz explanations share the viewer. Summary links open source coverage pages without claiming a precise supporting passage.

## Backend

- Existing page-aware chunks, stable chunk IDs and vector metadata are preserved. No Pinecone schema change or re-ingestion is needed.
- `app/citations/catalog.py` attaches canonical registry metadata before prompt budgeting. Only passages that fit the final prompt are registered and published.
- `store.py` persists source records in SQLite's `citation_sources` table. Source IDs include the document, knowledge base, chunk, passage, physical page and original file revision. Deleting a document removes its source records.
- The model receives `source_id` headers and cites `[[source_id]]`. `markers.py` buffers incomplete markers, accepts only supplied IDs, emits validated citation events, and converts accepted markers into internal Markdown references. Unknown IDs are omitted. Cancellation closes the underlying provider iterator.
- `/ask` SSE emits `sources` before text, then `citation` before its corresponding reference. Plain-text clients retain the existing response type; interactive source metadata requires SSE.
- `GET /citations/{id}?knowledge_base_id=local` resolves a persisted source and its page count.
- `GET /documents/{id}/pdf?knowledge_base_id=local` serves the original file inline, with byte-range support. Both endpoints check registry membership/readiness and original-file availability. File paths must resolve directly inside the upload directory; outside paths and escaping symlinks are rejected. Recovered records without `saved_path` may resolve an existing `{document_id}.pdf`; filenames are never guessed. Source resolution rejects changed files. Responses use private/no-store caching.

These checks follow the existing local knowledge-base model. The application does not currently have account authentication. A multi-user deployment must derive knowledge-base access from its authenticated principal; a caller-supplied knowledge-base name is not an account authorization boundary.

## Frontend

- `components/pdf/` contains the shared modal, PDF.js loading, page rendering, navigation, text layer and source buttons. Viewer modules are loaded on demand. Only the current page is rendered, and large PDFs use range loading.
- PDF.js worker, fonts, character maps and decoders are served locally via `pdfAssets.js`; opening a PDF does not require an external PDF service or CDN.
- Streamed metadata is retained outside React's conversation state until settlement. Citation buttons work in the unfinished streaming block and in completed Markdown. Bounded chat persistence retains validated citation metadata and counts its size toward the existing storage limit.
- Both `[[source_id]]` and `【source_id】` are validated incrementally. The frontend also converts known raw IDs in restored answers into compact numbered source buttons; unknown references never become viewer links. `MarkdownBlock.jsx` renders math and citations in both completed blocks and the streaming tail.
- The viewer resolves IDs through the backend rather than accepting a model-supplied URL or coordinates. It supports page navigation, zoom, responsive page fitting, selectable text, Escape to close and focus restoration.
- Phase 1 highlighting maps normalized PDF.js text back to actual DOM text nodes. A complete, unique passage of at least 24 normalized characters is required. Whitespace and ligatures are normalized; dehyphenation uses actual PDF.js line breaks. Minus signs and meaningful internal hyphens are preserved. The resulting DOM range supplies highlight rectangles, including rotated pages. Resizing and zooming rebuild the text layer and highlights.
- Repeated, absent, scanned or too-short passages open the page with the quote in the sidebar and no highlight. OCR and persisted word-coordinate highlighting are not implemented in this phase. Existing recovered documents without an available original file need re-uploading. Historical answers containing only free-form filename/page citations are not rewritten.
- Quiz cache version `sources_v2` refreshes old quizzes so their newly verified source records have resolvable IDs.

## Verification (2026-10-23)

- Backend: `.venv/bin/python -m unittest discover -s tests -t .` — 239 run, 237 passed; the two existing hierarchy tests still error because their PDF fixtures are missing.
- Frontend: `npm test` — 33 passed; `npm run lint` and `npm run build` passed.
- Local headless Chrome with synthetic PDFs: streaming/completed/quiz links, correct page, zoom, navigation, rotated highlights, repeated/blank-page fallbacks, mobile layout, Escape/focus restoration and byte-range navigation to page 269 passed. No uploaded PDF content was sent to an external model.
- API tests include namespace mismatch, non-ready/deleted/missing PDFs, changed files, symlinks, range errors, SSE event ordering and persisted citation resolution. Stream tests cover every marker split, unknown IDs, budget-excluded evidence and cancellation.

The two missing fixture paths are `backend/uploads/computer_science_sample.pdf` and `backend/uploads/Python_Smaller_Concepts_for_NLP_Practicals.pdf`.
