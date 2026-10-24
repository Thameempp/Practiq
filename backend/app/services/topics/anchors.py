import re
import unicodedata


def token(value: str) -> str:
    value = " ".join(unicodedata.normalize("NFC", value).casefold().split()).rstrip(":")
    return value.rstrip(".)") if re.fullmatch(r"\d+(?:\.\d+)*[.)]?", value) else value


def heading_position(title: str, text: str, minimum: int = 0) -> int | None:
    span = heading_span(title, text, minimum)
    return span[0] if span else None


def _symbols(text: str) -> list[tuple[str, int]]:
    return [(symbol, index) for index, word in enumerate(text.split())
            for symbol in re.findall(r"\w+|[^\w\s]", token(word))]


def heading_span(title: str, text: str, minimum: int = 0) -> tuple[int, int] | None:
    """Locate original words, including chapter numbers extracted after their title."""
    wanted = [symbol for symbol, _ in _symbols(title)]
    symbols = _symbols(text)
    values = [symbol for symbol, _ in symbols]
    if not wanted:
        return None
    matches = []
    for i in range(len(symbols) - len(wanted) + 1):
        end = i + len(wanted)
        if (symbols[i][1] >= minimum and values[i:end] == wanted
                and (i == 0 or symbols[i - 1][1] != symbols[i][1])
                and (end == len(symbols) or symbols[end][1] != symbols[end - 1][1])):
            matches.append((symbols[i][1], symbols[end - 1][1] + 1))
    numbered = re.fullmatch(r"(\d+(?:\.\d+)*)\.?\s+(.+)", title.strip())
    trailing = (re.compile(re.escape(token(numbered[2])) + r"\s*" + re.escape(numbered[1]))
                if numbered else None)
    headings, offset = [], 0
    for line in text.splitlines():
        size = len(line.split())
        if [symbol for symbol, _ in _symbols(line)] == wanted:
            headings.append((offset, offset + size))
        elif line.strip().casefold().startswith(title.casefold() + ":"):
            headings.append((offset, offset + len(title.split())))
        elif trailing and trailing.fullmatch(token(line)):
            headings.append((offset, offset + size))
        offset += size
    headings = [span for span in headings if span[0] >= minimum]
    if headings:
        return headings[0]
    return matches[0] if len(matches) == 1 else None
