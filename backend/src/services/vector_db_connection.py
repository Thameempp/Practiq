import os
import time
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from src.core.config import settings
from src.services.embedding_model import result
from src.services.clean import clean_text

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
my_vector = [0.012] * DIMENSION

vector_to_upsert = {
    'id': 'id_chunk1',
    'values':result.embeddings[0].values,
    'metadata':{
        'text': clean_text
    }
}

index.upsert(vectors=[vector_to_upsert])