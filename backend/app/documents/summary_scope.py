import re

WHOLE_DOCUMENT = re.compile(
    r"\b(?:this|that|the|my|uploaded|entire|whole|full|complete)\s+(?:pdf|document|file|book|paper)\b"
    r"|\b(?:all|every)\s+(?:the\s+)?pages?\b|\bfrom start to finish\b", re.I,
)


def whole_document_summary(question: str) -> bool:
    return bool(WHOLE_DOCUMENT.search(question))
