from app.services.chunk_ids import make_chunk_id
from app.services.chunk_store import add_chunks
from app.services.embedding import get_embeddings_batch
from app.services.pinecone_index import get_index


def ingest_chunks(chunks, document_id: str, filename: str, knowledge_base_id: str = "local"):
    # embed all chunks in a single API call instead of one call per chunk
    embeddings = get_embeddings_batch([chunk["text"] for chunk in chunks])

    vectors = [
        {
            'id': make_chunk_id(document_id, i),
            'values': embedding,
            'metadata': {
                "document_id": document_id,
                "knowledge_base_id": knowledge_base_id,
                "filename": filename,
                'text': chunk["text"],
                "page": chunk["page"],
                "chunk_index": i,
            }
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    get_index().upsert(vectors=vectors)
    add_chunks([
        {"id": vector["id"], "score": 0.0, "metadata": dict(vector["metadata"])}
        for vector in vectors
    ])
