import re


RE_NO_LETTERS = re.compile(r"[a-zA-Z]")
RE_MAJOR_NUMBERED = re.compile(r"^\d+\.\s+\S")
RE_NUMBERED_PREFIX = re.compile(r"^(\d+(?:\.\d+)*)(?:[\)\.]|\s)\s+(.+)$")
RE_LIST_NUMBER = re.compile(r"^\d+[\)\.]?\s*$")
RE_LEADING_LIST_NUMBER = re.compile(r"^(\d+)[\)\.]?\s+(.+)$")
RE_BULLET_MARKER = re.compile(r"^[•\-\u2022]$")
RE_BULLET_PREFIX = re.compile(r"^[•\-\u2022]\s*")
RE_ANSWER_CHOICE = re.compile(r"^[A-Da-d][\)\.]\s")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"(?<=\w)\s+-\s+(?=\w)", "-", text)


def is_bold(flags: int) -> bool:
    return bool(flags & 16)
