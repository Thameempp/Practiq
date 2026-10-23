import os 
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"
DATA_PATH = BACKEND_DIR / "data"

load_dotenv(dotenv_path=ENV_PATH)

@dataclass(frozen=True)
class Settings:
    BASE_DIR : Path = BACKEND_DIR
    DATA_DIR : Path = DATA_PATH

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")

    CORS_ORIGINS: tuple = ("http://localhost:5173", "http://127.0.0.1:5173")

    LLM_MODEL: str = "openai/gpt-oss-120b"
    EMBEDDING_MODEL: str = "gemini-embedding-2"
    RERANKER_MODEL: str = os.getenv(
        "RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    )
    RETRIEVAL_CANDIDATES: int = int(os.getenv("RETRIEVAL_CANDIDATES", "20"))
    EXPANDED_RETRIEVAL_CANDIDATES: int = int(os.getenv("EXPANDED_RETRIEVAL_CANDIDATES", "40"))
    FINAL_CONTEXT_CHUNKS: int = int(os.getenv("FINAL_CONTEXT_CHUNKS", "5"))


settings = Settings()
