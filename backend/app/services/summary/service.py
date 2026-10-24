"""Connect stored PDF text and the summary agent to the existing /ask response."""

import logging
from dataclasses import replace

from app.agents.pdf_summary_agent import PDFSummaryAgent
from app.services.summary.llm import make_generate_text
from app.services.summary.models import SummaryConfig, SummaryError
from app.services.summary.storage import load_summary_chunks
from app.services.summary.streaming import make_stream_generate_text
from app.services.summary.checkpoints import cached_generate
from app.services.summary.retry import call_with_retry
from app.services.summary.digest import prepare_source

logger = logging.getLogger(__name__)


def summarize_document(
    document_id,
    client,
    *,
    outline=None,
    request="",
    page_range=None,
    summary_type="comprehensive",
    on_text=None,
    on_progress=None,
) -> dict:
    chunks = load_summary_chunks(document_id)
    if page_range:
        chunks = [chunk for chunk in chunks if page_range[0] <= chunk["page"] <= page_range[1]]
    config = SummaryConfig()
    chunks, coverage, revision = prepare_source(chunks, config)
    compact = replace(config, max_summary_chars=config.intermediate_chars)
    generate = make_generate_text(client, config=compact)
    intermediate = cached_generate(
        document_id,
        lambda prompt: call_with_retry(generate, prompt, compact),
        compact,
        revision=revision,
    )
    final_generate = make_generate_text(client, config=config) if on_text is None else None
    final = (
        make_stream_generate_text(client, on_text, config)
        if on_text is not None
        else lambda prompt: call_with_retry(final_generate, prompt, config)
    )
    final = cached_generate(document_id, final, config, final=True, emit=on_text, revision=revision)
    agent = PDFSummaryAgent(
        intermediate,
        config=config,
        generate_final=final,
        on_progress=on_progress,
        retry_generation=False,
    )
    if summary_type in ("brief", "key_points"):
        request = f"[format={summary_type}]\n{request}"
    result = agent.summarize(chunks, outline=outline, request=request)
    result["coverage"] = coverage
    return result


def stream_document_summary(document_id, client, *, outline=None, request=""):
    try:
        result = summarize_document(document_id, client, outline=outline, request=request)
        yield result["summary"]
    except SummaryError as error:
        logger.warning("PDF summary failed: %s", error)
        yield f"⚠️ {error}"
    except Exception:
        logger.exception("Unexpected PDF summary failure")
        yield "⚠️ The PDF summary service is temporarily unavailable. Please try again."
