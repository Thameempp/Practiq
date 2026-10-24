DEFAULT_CHUNK_SIZE = 120
DEFAULT_OVERLAP = 30


def word_spans(length: int, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    if chunk_size < 1:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be greater than or equal to zero and less than chunk_size")

    for start in range(0, length, chunk_size - overlap):
        yield start, min(length, start + chunk_size)


def chunk_pages(pages, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    list(word_spans(0, chunk_size, overlap))
    chunks = []

    for page in pages:
        words = page["text"].split()
        for start, end in word_spans(len(words), chunk_size, overlap):
            chunk_words = words[start:end]

            if chunk_words:
                chunks.append({
                    "page": page["page"],
                    "text": " ".join(chunk_words)
                })

    return chunks
