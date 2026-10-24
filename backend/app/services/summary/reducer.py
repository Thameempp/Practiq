"""Merge small consecutive groups; singleton tails are carried forward."""

from app.services.summary.models import SummaryChunk, SummaryConfig, SummaryError
from app.services.summary.prompts import summary_prompt
from app.services.summary.budget import input_tokens


def reduce_summaries(notes, generate, config: SummaryConfig, *, outline=None, request="", generate_final=None):
    current = list(notes)
    while len(current) > 1:
        groups = _groups(current, config, outline, request)
        final = len(groups) == 1
        merged = []
        for group in groups:
            if len(group) == 1:
                merged.extend(group)
                continue
            prompt = summary_prompt(group, final=final, mapping=False, outline=outline if final else None,
                                    request=request if final else "", max_chars=config.max_summary_chars if final else config.intermediate_chars)
            operation = generate_final if final and generate_final is not None else generate
            merged.append(SummaryChunk(operation(prompt), group[0].page_start,
                                       max(note.page_end for note in group)))
        if len(merged) >= len(current):
            raise SummaryError("Summary merge budget is too small to combine two summaries.")
        current = merged
    return current[0].text


def _groups(notes, config, outline, request):
    groups, group = [], []
    for note in notes:
        candidate = [*group, note]
        prompt = summary_prompt(candidate, final=True, mapping=False, outline=outline,
                                request=request, max_chars=config.max_summary_chars)
        if group and (len(candidate) > config.max_summaries_per_group
                      or len(prompt.encode()) > config.max_prompt_bytes
                      or input_tokens(prompt) > config.max_input_tokens):
            groups.append(group)
            group = []
        group.append(note)
    if group:
        groups.append(group)
    return groups
