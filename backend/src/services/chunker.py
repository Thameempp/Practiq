# split data into smaller chunks 
def chunk_pages(pages, chunk_size=20):

    chunks = []

    for page in pages:
        words = page["text"].split()

        for start in range(0, len(words), chunk_size):
            chunk_words = words[start:start + chunk_size]

            if chunk_words:
                chunks.append({
                    "page":page["page"],
                    "text":" ".join(chunk_words)
                })

    return chunks