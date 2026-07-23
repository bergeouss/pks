from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from app.core.config import settings
from app.core.runtime_settings import get_runtime_settings
from typing import List
import logging

logger = logging.getLogger(__name__)


# Known embedding vector dimensions, keyed by model id (lowercase).
# Used by app.main startup to size the Qdrant collection correctly.
EMBEDDING_DIMENSIONS = {
    # OpenAI
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
    # Gemini
    "gemini-embedding-001": 3072,
    "gemini-embedding-2-preview": 3072,
    # Ollama (varies by model; these are the common defaults)
    "mxbai-embed-large": 1024,
    "nomic-embed-text": 768,
    "bge-m3": 1024,
}


def embedding_vector_size(provider: str, model: str) -> int:
    """Best-effort vector dimension for a (provider, model) pair."""
    if model and model.lower() in EMBEDDING_DIMENSIONS:
        return EMBEDDING_DIMENSIONS[model.lower()]
    # Provider-level fallbacks
    if provider == "openai":
        return 1536
    if provider == "gemini":
        return 3072
    if provider == "ollama":
        return 1024
    return 1536


class EmbeddingService:
    """Generate embeddings using multiple providers (OpenAI, Gemini, Ollama).

    Reads the active provider/model from the runtime override layer so the
    Settings UI can switch embedding model without a backend restart.
    """

    def __init__(self):
        self._cache_key = None
        self._embeddings = None

    @property
    def active(self):
        """Current (provider, model) after runtime overrides."""
        rt = get_runtime_settings()
        return rt["embedding_provider"], rt["embedding_model"]

    def _build(self, provider: str, model: str):
        if provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            # Gemini expects the "models/" prefix for the embedding API
            gemini_model = model if model.startswith("models/") else f"models/{model}"
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=gemini_model,
                google_api_key=settings.GEMINI_API_KEY,
            )
            logger.info(f"Initialized Gemini embeddings: {gemini_model}")
        elif provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self._embeddings = OpenAIEmbeddings(
                model=model or "text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY,
            )
            logger.info(f"Initialized OpenAI embeddings: {model}")
        elif provider == "ollama":
            self._embeddings = OllamaEmbeddings(
                model=model or "mxbai-embed-large",
                base_url=settings.OLLAMA_BASE_URL,
            )
            logger.info(f"Initialized Ollama embeddings: {model or 'mxbai-embed-large'}")
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    @property
    def embeddings(self):
        provider, model = self.active
        cache_key = (provider, model)
        if self._cache_key != cache_key or self._embeddings is None:
            self._build(provider, model)
            self._cache_key = cache_key
        return self._embeddings

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return await self.embeddings.aembed_query(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return await self.embeddings.aembed_documents(texts)


embedding_service = EmbeddingService()