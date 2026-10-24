import re

DOUBT = re.compile(
    r"^(?:(?:please|no|wait|but)[,!:]?\s+|(?:can|could|would) you\s+)*(?:"
    r"are you (?:really |absolutely )?sure\b|is (?:that|this|your answer) (?:really )?correct\b|"
    r"i (?:think|believe) (?:you(?:'re| are)|your (?:answer|explanation) is) (?:wrong|incorrect)\b|"
    r"(?:that(?:'s| is)|your (?:answer|explanation) is) (?:wrong|incorrect)\b|"
    r"(?:check|try|look) (?:it |that |this )?again\b|"
    r"(?:recheck|re-check|double[ -]check)\b|"
    r"(?:verify|validate|fact[ -]check)\s+(?:(?:the|your|that|this|previous|last)\s+)*"
    r"(?:answer|response|explanation|summary|calculation|claim|result)\b)", re.I)


def is_verification_request(question: str) -> bool:
    return bool(DOUBT.search(question.strip().replace("’", "'")))
