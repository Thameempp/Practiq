"""Local duplicate checks and bounded context for a fresh question's model prompt."""

import json
import re
import unicodedata
from collections.abc import Sequence
from difflib import SequenceMatcher

from app.services.mcq.errors import MCQGenerationError


class DuplicateQuestion(MCQGenerationError):
    def __init__(self, questions: Sequence[str] = ()) -> None:
        self.questions = list(questions)
        super().__init__("Could not create another distinct question from this topic. Practice is paused.")


def normalized_question(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def ensure_distinct(questions: Sequence[str], previous: Sequence[str]) -> None:
    known = [normalized_question(text) for text in previous]
    for text in questions:
        candidate = normalized_question(text)
        tokens = set(candidate.split())
        for old in known:
            other = set(old.split())
            overlap = len(tokens & other) / max(1, len(tokens | other))
            if candidate == old or overlap >= 0.8 or SequenceMatcher(None, candidate, old).ratio() >= 0.9:
                raise DuplicateQuestion(questions)
        known.append(candidate)


def novelty_context(previous: Sequence[str]) -> str:
    lines, remaining = [], 4000
    for text in reversed(previous):
        line = json.dumps(text[:1000], ensure_ascii=False) + "\n"
        if len(line) > remaining:
            continue
        lines.append(line)
        remaining -= len(line)
    return "".join(reversed(lines))
