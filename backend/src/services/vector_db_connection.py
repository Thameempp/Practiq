import os
from pinecone import Pinecorn, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from src.core.config import settings
from src.services.embedding_model import result
from src.services.clean import clean_text

pc = Pinecorn(api_key=settings.PINECONE_API_KEY)

index_name = 'rag-project-index'

# delete index if it is already exists
if index_name in pc.list_indexes().names():
    pc.delete_index(name=index_name)


# creat serverless index with correct dimension
pc.creat_index(
    name = index_name ,
    dimension=3072,
    matric='cosine',
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

index = pc.index(index_name)
DIMENSION = 3072
my_vector = [0.012] * DIMENSION

vector_to_upsert = {
    'id': 'id_chunk1',
    'values':result.embeddings[0].values,
    'metadata':{
        'text': clean_text
    }
}

index.upsert(vector=[vector_to_upsert])