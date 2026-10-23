from google import genai 
from src.core.config import settings

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

def get_embedding(text: str) -> list[float]:
    result = client.models.embed_content(
        model = settings.EMBEDDING_MODEL,
        contents = text
)
    return result.embeddings[0].values
