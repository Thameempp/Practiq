from google import genai 
from src.core.config import settings

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

result = client.models.embed_content(
    model = 'gemini-embedding-2',
    contents = 'clustering in machine learning'
)

print(result.embeddings)