from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using multiple providers (OpenAI, Gemini)"""

    def __init__(self):
        self.provider = settings.DEFAULT_EMBEDDING_PROVIDER
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            if self.provider == "gemini":
                if not settings.GEMINI_API_KEY:
                    raise ValueError("GEMINI_API_KEY not configured")
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004",
                    google_api_key=settings.GEMINI_API_KEY,
                )
                logger.info("Initialized Gemini embeddings (text-embedding-004)")
            else:  # openai
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not configured")
                self._embeddings = OpenAIEmbeddings(
                    model=settings.DEFAULT_EMBEDDING_MODEL,
                    openai_api_key=settings.OPENAI_API_KEY,
                )
                logger.info(f"Initialized OpenAI embeddings: {settings.DEFAULT_EMBEDDING_MODEL}")
        return self._embeddings

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return await self.embeddings.aembed_query(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return await self.embeddings.aembed_documents(texts)


embedding_service = EmbeddingService()
