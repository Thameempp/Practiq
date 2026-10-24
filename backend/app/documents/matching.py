import re

ORDINALS = {word: index for index, word in enumerate(("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"))}


def normalize(value):
    return " ".join(re.findall(r"\w+", re.sub(r"\.pdf\b", "", value, flags=re.I).casefold()))


def named_matches(reference, documents):
    if not reference:
        return []
    ref = re.sub(r"^(?:of|from|about)\s+|^(?:the|my|uploaded)\s+", "", reference.strip(), flags=re.I)
    ref = re.sub(r"\s+(?:pdf|file|document)$", "", ref, flags=re.I)
    # A full .pdf filename is explicit; a short title may match several files.
    exact = [doc for doc in documents if doc.filename.casefold() in ref.casefold()]
    if exact:
        return exact
    target = normalize(ref)
    return [doc for doc in documents if target and f" {target} " in f" {normalize(doc.filename)} "]


def ordinal_index(reference, *, pending=False):
    text = reference.casefold().strip(" .?!")
    match = re.search(r"\b(" + "|".join(ORDINALS) + r")(?:\s+(?:one|pdf|document|file))?\b", text)
    if match:
        return ORDINALS[match.group(1)]
    match = re.search(r"\b(\d+)(?:st|nd|rd|th)?\s+(?:pdf|document|file)\b", text)
    if match or pending and text.isdigit():
        return int(match.group(1) if match else text) - 1
    return None
