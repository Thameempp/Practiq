import re

PREFIX = r"^(?:(?:please|can you|could you|would you)\s+)?"
SUMMARY_ACTION = re.compile(PREFIX + r"(?:summari[sz]e|summari[sz]ation\b|tl;?\s?dr\b|in short\b|brief me\b)", re.I)
SUMMARY_NOUN = re.compile(r"^(?:(?:give|show|provide|write|create|make|need|want|get)(?: me)?\s+(?:an? |the )?)?(?:summary|overview|brief|executive summary)\b", re.I)
POINTS = re.compile(r"\b(?:key (?:takeaways?|points|ideas)|main (?:points|ideas|topics|themes))\b", re.I)
ALL_DOCUMENTS = re.compile(r"\b(?:all|every|each)\s+(?:(?:of|my|our|the|these|uploaded|one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+)*(?:pdfs?|documents?|files?)\b|\b(?:collection|entire knowledge base|whole knowledge base)\b|\b(?:my|our|these|the uploaded)\s+(?:pdfs|documents|files)\b", re.I)
DOC_REFERENCE = re.compile(r"\b(?:this|that|the|my|uploaded)\s+(?:pdf|document|file|book|paper)\b|\.pdf\b|\bchapter\s+\w+", re.I)
CHAPTER = re.compile(r"\bchapter\s+([\w.-]+)", re.I)
COMPARISON = re.compile(r"\b(?:compare|contrast|differences?|similarities)\b", re.I)
GENERIC = re.compile(r"^(?:(?:of|from|about)\s+)?(?:(?:this|that|the|my|a|uploaded|entire|whole|full|complete)\s+)*(?:pdf|document|file|book|paper)?[.?!\s]*$", re.I)
CONTEXTUAL = re.compile(r"\b(?:that (?:pdf|document|file|one)|the previous (?:pdf|document|file|one)|it)\b", re.I)


def reference_of(question):
    value = re.sub(r"^(?:please\s+)?(?:(?:can|could|would)(?: you| i)?\s+)?", "", question.strip(), flags=re.I)
    value = re.sub(r"^what are (?:the )?", "", value, flags=re.I)
    value = re.sub(r"^(?:give|show|provide|write|create|make|get)(?: me)?\s+", "", value, flags=re.I)
    value = re.sub(r"^(?:an? |the )?(?:summari[sz]e|summary|overview|executive summary|brief me|brief|tl;?dr|in short|key takeaways|key points|main points|main ideas)\s*(?:of|from|about)?\s*", "", value, flags=re.I)
    value = CHAPTER.sub("", value).strip(" .?!\"'")
    value = re.sub(r"^(?:all|every)(?: the)? pages?(?: (?:of|from))?\s*", "", value, flags=re.I)
    value = re.sub(r"\s*please$", "", value, flags=re.I).strip()
    return None if not value or GENERIC.fullmatch(value) else value
