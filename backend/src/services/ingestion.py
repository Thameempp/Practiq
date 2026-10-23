import time
from pinecone import Pinecone, ServerlessSpec
from src.core.config import settings
from src.services.embedding import get_embedding
from backend.src.services.cleaner import clean_text

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index_name = 'rag-project-index'
DIMENSION = 3072


existing_indexes = [idx.name for idx in pc.list_indexes()]


# creat serverless index with correct dimension
if index_name not in existing_indexes:
    pc.create_index(
        name = index_name ,
        dimension=3072,
        metric='cosine',
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)


index = pc.Index(index_name)

# ingest chunks to pinecone
def ingest_chunks(chunks):

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = get_embedding(chunk["text"])

        vectors.append({
            'id': f"chunk-{i}",
            'values':embedding,
            'metadata':{
                'text': chunk["text"],
                "page": chunk["page"]
                }
            })
    
    
    index.upsert(vectors=[vectors])