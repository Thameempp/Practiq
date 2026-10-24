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
    FINAL_CONTEXT_CHUNKS: int = int(os.getenv("FINAL_CONTEXT_CHUNKS", "6"))

    RETRIEVAL_CONTEXT_TOKENS: int = int(os.getenv("RETRIEVAL_CONTEXT_TOKENS", "6000"))
    RETRIEVAL_RESERVED_TOKENS: int = int(os.getenv("RETRIEVAL_RESERVED_TOKENS", "1000"))
    GENERATION_TOKENIZER_PATH: str = os.getenv("GENERATION_TOKENIZER_PATH", "")

    CHAT_CONTEXT_TOKENS: int = int(os.getenv("CHAT_CONTEXT_TOKENS", "16000"))
    CHAT_OUTPUT_TOKENS: int = int(os.getenv("CHAT_OUTPUT_TOKENS", "2048"))
    CHAT_HISTORY_TOKENS: int = int(os.getenv("CHAT_HISTORY_TOKENS", "2400"))
    CHAT_SAFETY_TOKENS: int = int(os.getenv("CHAT_SAFETY_TOKENS", "256"))
    CHAT_MEMORY_TOKENS: int = int(os.getenv("CHAT_MEMORY_TOKENS", "10000"))
    CHAT_MAX_TURNS: int = int(os.getenv("CHAT_MAX_TURNS", "12"))
    CHAT_TTL_SECONDS: int = int(os.getenv("CHAT_TTL_SECONDS", "86400"))
    SUMMARY_INPUT_TOKENS: int = int(os.getenv("SUMMARY_INPUT_TOKENS", "5500"))
    SUMMARY_OUTPUT_TOKENS: int = int(os.getenv("SUMMARY_OUTPUT_TOKENS", "2048"))
    SUMMARY_MAX_TIMEOUT_SECONDS: int = int(os.getenv("SUMMARY_MAX_TIMEOUT_SECONDS", "7200"))
    SUMMARY_MODEL: str = os.getenv("SUMMARY_MODEL", LLM_MODEL)
    SUMMARY_REQUESTS_PER_MINUTE: int = int(os.getenv("SUMMARY_REQUESTS_PER_MINUTE", "20"))
    SUMMARY_TOKENS_PER_MINUTE: int = int(os.getenv("SUMMARY_TOKENS_PER_MINUTE", "8000"))
    SUMMARY_DIGEST_THRESHOLD_PAGES: int = int(os.getenv("SUMMARY_DIGEST_THRESHOLD_PAGES", "80"))
    SUMMARY_PAGE_DIGEST_CHARS: int = int(os.getenv("SUMMARY_PAGE_DIGEST_CHARS", "900"))


    def __post_init__(self):
        if (self.CHAT_OUTPUT_TOKENS < 1 or self.CHAT_SAFETY_TOKENS < 128
                or self.CHAT_CONTEXT_TOKENS - self.CHAT_OUTPUT_TOKENS - self.CHAT_SAFETY_TOKENS < 2048
                or self.CHAT_HISTORY_TOKENS < 0 or self.CHAT_MEMORY_TOKENS < 4096
                or self.CHAT_MAX_TURNS < 1 or self.CHAT_TTL_SECONDS < 1):
            raise ValueError("Invalid chat context, output or retention limits.")
        if self.SUMMARY_INPUT_TOKENS < 2048 or self.SUMMARY_OUTPUT_TOKENS < 128 or self.SUMMARY_MAX_TIMEOUT_SECONDS < 600:
            raise ValueError("Invalid summary input, output or timeout limits.")
        if self.SUMMARY_REQUESTS_PER_MINUTE < 1 or self.SUMMARY_TOKENS_PER_MINUTE < self.SUMMARY_OUTPUT_TOKENS + 2048:
            raise ValueError("Invalid summary provider request/token rate limits.")


settings = Settings()
