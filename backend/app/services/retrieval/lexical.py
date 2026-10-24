import re

# Remove conversational filler; keep negation, quantities and technical vocabulary.
STOP_WORDS = frozenset("""
a an the is are was were be been being do does did of to from for in on at by
with as and or that this these those it its what which who when where why how
please explain describe give tell show me about can could would should i you
""".split())


def terms(text: str) -> list[str]:
    return [token for token in re.findall(r"\w+", text.casefold()) if token not in STOP_WORDS]
