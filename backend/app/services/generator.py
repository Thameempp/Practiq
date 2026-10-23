import time

from groq import Groq
from google.genai.errors import ServerError as GeminiServerError

from app.core.config import settings
from app.services.context import (
    build_retrieved_context,
    expand_with_neighbor_chunks,
    normalize_question,
)
from app.services.hierarchy import (
    build_scope_prompt,
    build_scope_search_text,
    parse_scope,
)
from app.services.document_summary import (
    SUMMARY_CHAR_BUDGET,
    SUMMARY_CHUNKS,
    pick_summary_chunks,
)
from app.services.reranker import rerank_chunks
from app.services.summary_intent import is_summary_request
from app.services.vector_search import hybrid_search


client = Groq(api_key = settings.GROQ_API_KEY)
NOT_FOUND_MESSAGE = "I cannot find that information in the document."

QA_SYSTEM_PROMPT = (
    "You are a document question-answering assistant.\n\n"
    "Use the rules below:\n"
    "1. Answer using the context provided from the uploaded PDF documents in the user message.\n"
    "2. If the context contains relevant information, answer directly from it.\n"
    "3. Cite document names and page numbers when they are available.\n"
    "4. Only if none of the context is relevant to the question, say exactly: "
    f"'{NOT_FOUND_MESSAGE}'"
)
SUMMARY_SYSTEM_PROMPT = (
    "You are a document summarization assistant.\n\n"
    "Use the rules below:\n"
    "1. The user message may contain a DOCUMENT OUTLINE (chapter and section titles) and "
    "PASSAGES sampled from across the document in page order. They are a sample, not the full text.\n"
    "2. Summarize the main subject matter: what the document is about, its major topics in order, "
    "and its key ideas or conclusions. Use the outline for structure and the passages for substance.\n"
    "3. Ignore copyright notices, publisher or website information, legal disclaimers, licences, "
    "acknowledgements, tables of contents, indexes and similar boilerplate. Never summarize or mention them.\n"
    "4. Do not describe the passages or the file itself (no 'the provided passage', no 'this PDF is a copy of'). "
    "Do not include page numbers, page links or citations.\n"
    "5. Format: a 2-3 sentence overview, then 'Main topics' as a short bullet list with one line per "
    "major topic, then 'Key takeaways' with 3-5 bullets. Use only what the outline and passages support."
)
MAX_OUTLINE_TITLES = 60
MAX_OUTLINE_TITLE_CHARS = 120


def retrieve_context(user_question: str, scope=None, document_id: str | None = None):
    print("retrieving top chunks", flush=True)
    parsed_scope = parse_scope(scope)
    document_id = (parsed_scope.document_id if parsed_scope else "") or document_id
    scope_search_text = build_scope_search_text(parsed_scope)
    retrieval_query = (
        f"{scope_search_text} {user_question}"
        if scope_search_text
        else user_question
    )
    candidates = hybrid_search(
        retrieval_query,
        top_k=settings.RETRIEVAL_CANDIDATES,
        document_id=document_id,
    )
    expanded_candidates = expand_with_neighbor_chunks(
        candidates,
        window=1,
        max_chunks=settings.EXPANDED_RETRIEVAL_CANDIDATES,
    )
    reranked_chunks = rerank_chunks(
        retrieval_query,
        expanded_candidates,
        top_k=settings.FINAL_CONTEXT_CHUNKS,
    )
    context_chunks = expand_with_neighbor_chunks(
        reranked_chunks,
        window=1,
        max_chunks=settings.FINAL_CONTEXT_CHUNKS + 4,
    )
    print("top chunks :", flush=True)
    for index, chunk in enumerate(context_chunks, start=1):
        metadata = chunk.get("metadata") or {}
        page = metadata.get("page", "unknown")
        chunk_index = metadata.get("chunk_index", "unknown")
        text = metadata.get("text") or chunk.get("text", "")
        preview = " ".join(str(text).split())[:200]
        print(f"\n{index}. page {page}, chunk {chunk_index}\n{preview}", flush=True)
    return context_chunks


def ask_pdf(
    user_question: str,
    scope=None,
    document_id: str | None = None,
    outline: list[str] | None = None,
):
    normalized_question, legacy_scope = normalize_question(user_question)
    parsed_scope = parse_scope(scope) or parse_scope(legacy_scope)
    summary_mode = (
        bool(document_id)
        and parsed_scope is None
        and is_summary_request(normalized_question)
    )

    try:
        if summary_mode:
            chunks = pick_summary_chunks(document_id)
            pages = sorted({(c.get("metadata") or {}).get("page") for c in chunks} - {None})
            print(f"summary: {len(chunks)} passages from pages {pages}", flush=True)
        else:
            chunks = retrieve_context(normalized_question, parsed_scope, document_id)
    except GeminiServerError as e:
        print(f"[ask_pdf] embedding service unavailable: {e}", flush=True)
        yield "⚠️ The embedding service is temporarily unavailable. Please try again in a few seconds."
        return
    except Exception as e:
        print(f"[ask_pdf] retrieval error: {e}", flush=True)
        yield f"⚠️ Could not retrieve context: {e}"
        return

    if summary_mode:
        system_prompt = SUMMARY_SYSTEM_PROMPT
        context_text = build_retrieved_context(
            chunks,
            max_chunks=SUMMARY_CHUNKS,
            max_total_chars=SUMMARY_CHAR_BUDGET,
        )
        outline_text = _outline_text(outline)
        user_prompt = (
            (f"DOCUMENT OUTLINE:\n{outline_text}\n\n" if outline_text else "")
            + f"PASSAGES:\n{context_text}\n\nREQUEST:\n{normalized_question}"
        )
    else:
        system_prompt = QA_SYSTEM_PROMPT
        user_prompt = (
            f"PDF CONTEXT:\n{build_retrieved_context(chunks)}\n\n"
            f"QUESTION:\n{normalized_question}"
        )
        scope_prompt = build_scope_prompt(parsed_scope)
        if scope_prompt:
            user_prompt += f"\n\nSELECTED HIERARCHY FOCUS:\n{scope_prompt}"

    print("passing top chunks to llm", flush=True)
    yield from _stream_answer(system_prompt, user_prompt)


def _outline_text(outline: list[str] | None) -> str:
    titles = [
        title.strip()[:MAX_OUTLINE_TITLE_CHARS]
        for title in (outline or [])[:MAX_OUTLINE_TITLES]
        if title and title.strip()
    ]
    return "\n".join(f"- {title}" for title in titles)


def _stream_answer(system_prompt: str, user_prompt: str):
    try:
        raw_response = client.chat.completions.with_raw_response.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=settings.LLM_MODEL,
            stream=True,
            extra_body={"stream_options": {"include_usage": True}}
        )

        streamed_answer = []
        for chunk in raw_response.parse():
            if chunk.choices:
                content = chunk.choices[0].delta.content

                if content:
                    streamed_answer.append(content)
                    yield content
                    time.sleep(0.04)
        print(f"llm streamed answer: {''.join(streamed_answer)}", flush=True)

    except Exception as e:
        print(f"[ask_pdf] LLM error: {e}", flush=True)
        yield f"⚠️ LLM error: {e}"
