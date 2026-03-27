from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "knowledge_base"

    # LLM Providers
    DEFAULT_LLM_PROVIDER: Literal["openai", "deepseek", "anthropic", "ollama", "zai"] = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    ZAI_API_KEY: str = ""
    ZAI_BASE_URL: str = "https://api.z.ai/api/coding/paas/v4"

    # Embedding
    DEFAULT_EMBEDDING_PROVIDER: Literal["openai", "gemini", "ollama"] = "gemini"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_API_KEY: str = ""

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # RAG
    TOP_K_RESULTS: int = 5

    # Frontend
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file


settings = Settings()
