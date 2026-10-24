"""Retrieve source-traceable evidence; answer generation stays outside this agent."""

from app.agents.base import BaseAgent
from app.orchestration.errors import TaskCancelled, TaskDeadline
from app.services.retrieval.candidates import clean_candidates
from app.services.retrieval.models import RetrievalConfig, RetrievalError
from app.services.retrieval.context import expand_candidates, format_context, select_context
from app.services.retrieval.observability import retrieval_result, timed_call
from app.services.retrieval.ranking import rank_candidates, reciprocal_rank_fusion
from app.services.retrieval.structure_evidence import supplement_candidates


class RetrievalAgent(BaseAgent[dict]):
    def __init__(
        self,
        dense_search,
        bm25_search,
        rerank,
        count_tokens,
        *,
        config: RetrievalConfig | None = None,
        fetch_neighbors=None,
        authorize_document=None,
    ):
        self.dense_search, self.bm25_search, self.rerank = (
            dense_search,
            bm25_search,
            rerank,
        )
        self.count_tokens, self.fetch_neighbors = count_tokens, fetch_neighbors
        self.authorize_document = authorize_document
        self.config = config or RetrievalConfig()


    def retrieve(self, question: str, document_id: str, *, search_query=None, topic_context=None) -> dict:
        return self.run(question, document_id, search_query=search_query, topic_context=topic_context)


    def _run(self, question: str, document_id: str, *, search_query=None, topic_context=None) -> dict:
        if not isinstance(question, str) or not isinstance(document_id, str):
            raise ValueError("A question and document ID are required.")
        question, document_id = question.strip(), document_id.strip()
        if not question or not document_id:
            raise ValueError("A question and document ID are required.")
        if self.authorize_document is not None and not self.authorize_document(document_id):
            raise PermissionError("Access to this document was denied.")
        query, config = search_query or question, self.config
        stats = dict.fromkeys(
            (
                "dense_candidates",
                "bm25_candidates",
                "fused_candidates",
                "expanded_candidates",
                "reranked_candidates",
                "selected_chunks",
            ),
            0,
        )
        stats.update(
            context_tokens=0,
            available_tokens=config.max_context_tokens - config.reserved_tokens,
        )
        timings = {}
        options = {"topic_context": topic_context} if topic_context else {}
        try:
            dense = timed_call(
                "dense", timings, self.dense_search, query,
                top_k=config.dense_top_k, document_id=document_id, **options,
            )
            sparse = timed_call(
                "bm25", timings, self.bm25_search, query,
                top_k=config.bm25_top_k, document_id=document_id, **options,
            )
            if topic_context:
                dense, sparse = topic_context.apply(dense), topic_context.apply(sparse)
            dense = clean_candidates(dense, document_id)[:config.dense_top_k]
            sparse = clean_candidates(sparse, document_id)[:config.bm25_top_k]
            stats.update(dense_candidates=len(dense), bm25_candidates=len(sparse))
            fused = timed_call("fusion", timings, reciprocal_rank_fusion, dense, sparse, k=config.rrf_k)
            fused = timed_call("structure", timings, supplement_candidates, fused, topic_context, document_id, config)
            stats["structure_candidates"] = sum("structure_rank" in c.get("retrieval", {}) for c in fused)
            stats["fused_candidates"] = len(fused)
            if not fused:
                return retrieval_result(question, [], stats, timings, reason="no_candidates")
            expanded = timed_call(
                "neighbors", timings, expand_candidates, fused,
                self.fetch_neighbors, document_id, config, **options,
            )
            stats["expanded_candidates"] = len(expanded)
            pairs = timed_call("rerank", timings, self.rerank, question, expanded)
            ranked = rank_candidates(
                pairs,
                expanded,
                limit=config.rerank_top_k,
                minimum=config.min_rerank_score,
            )
            stats["reranked_candidates"] = len(ranked)
            selected = timed_call("selection", timings, select_context, ranked, self.count_tokens, config)
            stats["context_tokens"] = self.count_tokens(format_context(selected))
            reason = (
                None if selected
                else "context_budget_exceeded" if ranked
                else "no_relevant_chunks"
            )
            return retrieval_result(question, selected, stats, timings, reason=reason)
        except (TaskCancelled, TaskDeadline):
            raise
        except RetrievalError:
            raise
        except Exception as error:
            raise RetrievalError("Document evidence could not be retrieved. Please try again.") from error
