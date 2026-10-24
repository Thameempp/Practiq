import time

from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.orchestration.runtime import check_active

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index_name = 'rag-project-index'
DIMENSION = 3072

# Lazily initialised — avoids crashing the module on import if the
# Pinecone API is temporarily unreachable (e.g. after a hot-reload).
_index = None


def get_index():
    check_active()
    global _index
    if _index is not None:
        return _index

    existing_indexes = [idx.name for idx in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=DIMENSION,
            metric='cosine',
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        while True:
            check_active()
            if pc.describe_index(index_name).status["ready"]:
                break
            time.sleep(1)

    _index = pc.Index(index_name)
    return _index
