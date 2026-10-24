from dataclasses import dataclass


class RetrievalError(RuntimeError):
    """One retrieval stage failed; the result must not be treated as no evidence."""


@dataclass(frozen=True)
class RetrievalConfig:
    dense_top_k: int = 20
    bm25_top_k: int = 20
    rerank_top_k: int = 20
    final_top_k: int = 6
    max_candidates: int = 40
    rrf_k: int = 60
    max_context_tokens: int = 6000
    reserved_tokens: int = 1000
    neighbor_window: int = 1
    min_rerank_score: float | None = None
    diversity_weight: float = 0.15


    def __post_init__(self):
        positive = (self.dense_top_k, self.bm25_top_k, self.rerank_top_k,
                    self.final_top_k, self.max_candidates, self.rrf_k)
        if any(value < 1 for value in positive):
            raise ValueError("Retrieval limits must be positive.")
        if not 0 <= self.reserved_tokens < self.max_context_tokens or self.neighbor_window < 0:
            raise ValueError("Invalid retrieval context budget or neighbor window.")
        if not 0 <= self.diversity_weight <= 0.5:
            raise ValueError("Retrieval diversity weight must be between zero and 0.5.")
