"""One task per PDF; consolidation depends on every requested summary succeeding."""

from app.services.summary.multi_document import consolidate_summaries
from app.services.summary.service import summarize_document
from app.orchestration.runtime import report_progress
from app.citations.summary import summary_source
from app.services.summary.coverage import coverage_note


def summarize_pdf(decision, document, client, context):
    published = False


    def emit(text):
        nonlocal published
        if not published:
            context.emit(f"\n\n## {document.filename}\n\n")
            published = True
        context.emit(text)

    kind = {"brief": "Give a brief overview.", "key_points": "Focus on key points and takeaways.",
            "comprehensive": "Cover the main topics comprehensively.", "chapter": "Summarize only this chapter."}
    result = summarize_document(document.document_id, client,
        outline=[node["title"] for node in document.hierarchy],
        request=kind[decision.analysis.summary_type] + " " + decision.question,
        page_range=decision.page_range, summary_type=decision.analysis.summary_type,
        on_text=emit, on_progress=report_progress)
    context.check()
    context.evidence.extend({"document_id": document.document_id,
                             "page_start": note["page_start"], "page_end": note["page_end"]}
                            for note in result.get("chunk_summaries", []))
    context.emit(render_summary(document.filename, result, include_body=not published))
    context.emit(summary_source(document, result))
    return {"filename": document.filename, **result}


def render_summary(filename, result, *, include_body=True):
    text = f"\n\n## {filename}\n\n{result['summary']}\n" if include_body else "\n"
    ranges = sorted({(note["page_start"], note["page_end"]) for note in result.get("chunk_summaries", [])})
    if ranges:
        pages = ", ".join(str(start) if start == end else f"{start}–{end}" for start, end in ranges)
        text += f"\nSource coverage: {filename}, PDF pages {pages}.\n"
    return text + coverage_note(result.get("coverage", {}))


def consolidate(context, task_ids, client):
    published = False


    def emit(text):
        nonlocal published
        if not published:
            context.emit("\n\n## Combined summary\n\n")
            published = True
        context.emit(text)

    summaries = [(context.outputs[key]["filename"], context.outputs[key]["summary"]) for key in task_ids]
    result = consolidate_summaries(summaries, client, on_text=emit)
    context.check()
    context.emit("\n" if published else f"\n\n## Combined summary\n\n{result}\n")
    return result
