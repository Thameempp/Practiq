import logging
from time import perf_counter

from app.orchestration.runtime import check_active
from app.services.retrieval.context import format_context

logger = logging.getLogger(__name__)


def timed_call(stage, timings, operation, *args, **kwargs):
    start = perf_counter()
    try:
        check_active()
        result = operation(*args, **kwargs)
        check_active()
        return result
    finally:
        timings[stage] = round((perf_counter() - start) * 1000, 3)


def retrieval_result(question, chunks, stats, timings, *, reason=None):
    stats["selected_chunks"] = len(chunks)
    logger.info("Retrieval counts=%s latency_ms=%s scores=%s", stats, timings,
                [chunk["rerank_score"] for chunk in chunks])
    result = {"question": question, "status": "no_results" if reason else "success",
              "chunks": chunks, "context": format_context(chunks),
              "retrieval_stats": stats, "latency_ms": timings}
    if reason:
        result["reason"] = reason
    return result
