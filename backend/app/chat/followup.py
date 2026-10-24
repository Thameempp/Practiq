"""Resolve conversational references without another model request."""

import re

from app.chat.tokens import clip_tokens

REFERENCE = re.compile(
    r"\b(?:it|its|they|them|their|this|that|these|those|above|previous|earlier)\b"
    r"|^(?:why|how|continue|go on|more(?: details?)?|examples?|elaborate|explain more|give (?:me )?an example)[?.!\s]*$"
    r"|^(?:list|name|explain|describe|show|expand|give|what (?:are|were|is))\s+(?:me\s+)?the\s+"
    r"(?:(?:\d+|two|three|four|five|six|main|different)\s+)?(?:levels?|steps?|stages?|points?|types?|components?|examples?)\b"
    r"|\b(?:first|second|third|fourth|last)\s+(?:one|level|point|step|item)\b",
    re.I,
)


def is_followup(question: str) -> bool:
    return bool(REFERENCE.search(question))


def contextual_query(question, turns):
    if not turns or not is_followup(question):
        return clip_tokens(question, 2000), clip_tokens(question, 600)
    last = turns[-1]
    topic = last["topic"]
    previous = clip_tokens(last["answer"], 300)
    query = (f"Follow-up question: {clip_tokens(question, 1000)}\nTopic: {clip_tokens(topic, 600)}"
             f"\nPrevious answer (reference only): {previous}")
    return query, topic
