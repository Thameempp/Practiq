# Project cleanup — S-025

The workspace keeps its existing PDF, chat, summary, citation and practice contracts.

## Structure

- Frontend `App.jsx` is 617 lines, down from 1,094. Composer and table rendering are components; upload lifecycle, persistence, theme, health, scrolling and motion have dedicated hooks.
- `frontend/src/services/` holds the shared API URL, document API, serialized upload queue, storage, scope and scroll helpers. `PracticeArena`, verification and PDF viewing share the API configuration.
- Backend callers import `get_orchestrator` from `app.orchestration.service`. Internal tests use `executor.py`; the unused misspelled compatibility module is removed.
- Production requirements declare direct SDK/framework imports. Unused LangChain, NLTK, spaCy, pinecone-text and duplicate uvicorn entries are removed. `requirements-dev.txt` adds the test HTTP client. No installed packages were changed; a clean dependency installation has not been exercised.

## Logic corrections

- File uploads run sequentially across batches. Pending state remains active until every queued upload settles; one failed upload does not block later files.
- Backend availability follows health checks; a generation failure no longer marks a healthy server offline.
- Bulk deletion waits for all requests and removes only successfully deleted PDFs from the UI. Failed documents remain available for retry.
- Legacy retrieval preserves cancellation/deadlines. Retrieval and embedding logs record error types rather than raw provider bodies; retrieval failures return safe retry text.
- Scroll listeners, animation frames, request timeouts and composer animations have lifecycle cleanup. Optional browser storage cannot prevent theme changes or workspace use.

## Removed after checking references

- Empty `backend/app/api/agents_routes.py` and `backend/app/routes/query.py`.
- Unused `backend/app/utils/usage.py` and `backend/app/orchestration/executer.py`.
- Unused frontend demo `data/practiceData.js`, `data/documentHierarchy.js` and template `assets/react.svg`, `assets/vite.svg`.

User PDFs, database contents, active branding assets and unrelated existing changes are preserved.

## Verification

- Frontend: 58 tests pass; lint and production build pass. The existing bundle-size advisory remains.
- Backend: 370 of 372 tests pass. Both remaining errors reproduce the baseline missing hierarchy PDF fixtures (`computer_science_sample.pdf`, `Python_Smaller_Concepts_for_NLP_Practicals.pdf`).
- Added behavior tests for upload serialization/failure recovery, safe storage, bounded document scope, scroll following, restored application rendering, partial deletion and retrieval cancellation/error handling.
- No live LLM, embedding or vector-store requests were made. Browser interaction and a fresh dependency installation remain unverified.
