"""Pack pre-extracted text in page order without sampling or dropping content."""

from app.services.summary.models import SummaryChunk, SummaryConfig, SummaryError
from app.services.summary.budget import source_tokens
from app.chat.tokens import clip_tokens
from app.services.retrieval.tokens import count_tokens


def prepare_chunks(chunks, config: SummaryConfig, *, outline=None, request="") -> list[SummaryChunk]:
    ordered = []
    for index, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        if not isinstance(text, str):
            raise SummaryError("Summary chunk text must be a string.")
        if not text.strip():
            continue
        start = _page(chunk.get("page_start", chunk.get("page")))
        end = _page(chunk.get("page_end", start))
        if end < start:
            raise SummaryError("A summary chunk has an invalid page range.")
        ordered.append((start, index, text.strip(), end))

    packed = []
    byte_limit = config.max_prompt_bytes // 2
    token_limit = source_tokens(config, outline, request)
    for start, _, text, end in sorted(ordered):
        for piece in _split(text, config.max_chunk_chars, byte_limit, token_limit):
            previous = packed[-1] if packed else None
            combined = f"{previous.text}\n\n{piece}" if previous else piece
            if (previous and len(combined) <= config.max_chunk_chars and len(combined.encode()) <= byte_limit
                    and count_tokens(combined) <= token_limit):
                packed[-1] = SummaryChunk(combined, previous.page_start, max(previous.page_end, end))
            else:
                packed.append(SummaryChunk(piece, start, end))
    if not packed:
        raise SummaryError("No extracted PDF text is available to summarize.")
    return packed


def _split(text: str, char_limit: int, byte_limit: int, token_limit: int):
    while text:
        piece = text[:char_limit].encode()[:byte_limit].decode("utf-8", errors="ignore")
        piece = clip_tokens(piece, token_limit)
        if len(piece) < len(text):
            space = piece.rfind(" ")
            if space > len(piece) // 2:
                piece = piece[:space]
        yield piece
        text = text[len(piece):].lstrip()


def _page(value) -> int:
    try:
        page = int(value)
        if isinstance(value, bool) or page < 1 or float(value) != page:
            raise ValueError
        return page
    except (TypeError, ValueError, OverflowError) as error:
        raise SummaryError("Summary chunks require actual PDF page numbers.") from error
