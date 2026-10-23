from src.services.embedding import get_embedding
from backend.src.services.ingestion import index


def search_vector(query_text: str, top_k: int=10):

    query_vector = get_embedding(query_text)

    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    return response.get('matches', [])

def search_bm25(bm25, chunks, query_text: str, top_k: int = 10):
    
    tokenized_query = query_text.lower().split()

    scores = bm25.get_scores(tokenized_query)

    ranked_chunks = sorted(
        zip(chunks, scores),
        key = lambda x: x[1],
        reverse=True
    )

    return[
        {
            "chunk": chunk,
            "score": score
        }

        for chunk, score in ranked_chunks[:top_k]

    ]