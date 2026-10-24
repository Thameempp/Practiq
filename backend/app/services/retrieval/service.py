"""Create one configured agent and expose evidence and legacy chunk-list interfaces."""

from time import perf_counter

from app.agents.retrieval_agent import RetrievalAgent
from app.core.config import settings
from app.services.chunk_store import get_chunks_by_indexes
from app.services.reranker import rerank_chunks
from app.services.retrieval.dense import search_vector
from app.services.retrieval.models import RetrievalConfig
from app.services.retrieval.query import prepare_query
from app.services.retrieval.sparse import search_sparse
from app.services.retrieval.corpus import original_chunks
from app.services.retrieval.tokens import count_tokens, token_count_method
from app.services.retrieval.understanding import resolve_retrieval_context


def rerank_evidence(question, candidates):
    return [(chunk, chunk["rerank_score"]) for chunk in rerank_chunks(question, candidates)]


def fetch_neighbors(candidates, *, document_id, window):
    indexes = {neighbor for chunk in candidates if chunk["chunk_index"] is not None
               for neighbor in range(max(0, chunk["chunk_index"] - window),
                                     chunk["chunk_index"] + window + 1)}
    original = original_chunks(document_id)
    if original is not None:
        return [chunk for chunk in original if chunk["metadata"]["chunk_index"] in indexes]
    return get_chunks_by_indexes(sorted(indexes), document_id=document_id)


retrieval_agent = RetrievalAgent(
    dense_search=search_vector, bm25_search=search_sparse, rerank=rerank_evidence,
    count_tokens=count_tokens, fetch_neighbors=fetch_neighbors,
    config=RetrievalConfig(
        dense_top_k=settings.RETRIEVAL_CANDIDATES, bm25_top_k=settings.RETRIEVAL_CANDIDATES,
        max_candidates=settings.EXPANDED_RETRIEVAL_CANDIDATES,
        final_top_k=settings.FINAL_CONTEXT_CHUNKS,
        max_context_tokens=settings.RETRIEVAL_CONTEXT_TOKENS,
        reserved_tokens=settings.RETRIEVAL_RESERVED_TOKENS,
    ),
)


def retrieve_evidence(user_question, scope=None, document_id=None):
    query = prepare_query(user_question, scope, document_id)
    started = perf_counter()
    topics = resolve_retrieval_context(query.document_id, query.scope, query.question)
    understanding_ms = round((perf_counter() - started) * 1000, 3)
    search, options = query.search_text, {}
    if topics:
        nodes = [topics.selected] if topics.selected else topics.preferred
        focus = " ".join(" > ".join(node["path"]) for node in nodes)[:1000]
        search = f"{query.question} {focus}".strip()
        options["topic_context"] = topics
    result = retrieval_agent.retrieve(query.question, query.document_id, search_query=search, **options)
    result["topic_scope"] = ({"id": topics.selected["id"], "path": topics.selected["path"]}
                             if topics and topics.selected else None)
    result["retrieval_stats"]["token_counter"] = token_count_method()
    result["retrieval_stats"]["understanding_map"] = hasattr(topics, "document_map")
    result["latency_ms"]["understanding"] = understanding_ms
    return result


def retrieve_context(user_question, scope=None, document_id=None):
    return retrieve_evidence(user_question, scope, document_id)["chunks"]
