"""BM25 over the same document, including after a backend restart."""

from rank_bm25 import BM25L

from app.services.chunk_store import get_current_chunks
from app.services.pinecone_index import get_index
from app.services.retrieval.candidates import clean_candidates
from app.services.stored_chunks import read_stored_chunks
from app.services.stored_chunks import DocumentStoreError
from app.services.pdf_source import complete_chunks
from app.services.retrieval.corpus import original_chunks
from app.services.retrieval.lexical import terms
from app.services.retrieval.diversity import lexical_top


def search_sparse(query_text: str, top_k: int = 20, document_id: str = "", *, topic_context=None) -> list[dict]:
    if not document_id or not query_text.strip() or top_k < 1:
        raise ValueError("BM25 requires a document, query terms, and positive top_k.")
    query = terms(query_text)
    if not query:
        return []
    chunks = original_chunks(document_id)
    if chunks is None:
        chunks = get_current_chunks(document_id)
        if not complete_chunks(chunks, document_id):
            chunks = read_stored_chunks(document_id, get_index())
            if not complete_chunks(chunks, document_id):
                raise DocumentStoreError("The indexed PDF is incomplete. Upload the original PDF again.")
    candidates = clean_candidates(chunks, document_id)
    if topic_context:
        candidates = topic_context.apply(candidates)
    corpus = [terms(chunk["text"]) for chunk in candidates]
    if not candidates or not any(corpus):
        return []
    scores = BM25L(corpus).get_scores(query)
    matching = set(query)
    ranked = [{**chunk, "score": float(score)}
              for chunk, tokens, score in zip(candidates, corpus, scores)
              if matching.intersection(tokens)]
    return lexical_top(ranked, top_k)
