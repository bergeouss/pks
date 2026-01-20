from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProviderService:
    """Multi-provider LLM service using LangChain"""

    def __init__(self):
        self._current_provider = None
        self._llm = None

    def get_llm(self, provider: str = None, model: str = None):
        """Get LLM instance for specified provider"""
        provider = provider or settings.DEFAULT_LLM_PROVIDER

        # Return cached LLM if provider hasn't changed
        if self._current_provider == provider and self._llm:
            return self._llm

        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or "gpt-4o-mini",
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.7,
            )
        elif provider == "deepseek":
            if not settings.DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or "deepseek-chat",
                openai_api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1",
                temperature=0.7,
            )
        elif provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self._llm = ChatAnthropic(
                model=model or "claude-3-haiku-20240307",
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7,
            )
        elif provider == "ollama":
            self._llm = ChatOpenAI(
                model=model or "llama3",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.7,
            )
        elif provider == "zai":
            if not settings.ZAI_API_KEY:
                raise ValueError("ZAI_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or "glm-4.7",
                openai_api_key=settings.ZAI_API_KEY,
                base_url=settings.ZAI_BASE_URL,
                temperature=0.7,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        self._current_provider = provider
        logger.info(f"Initialized LLM with provider: {provider}")
        return self._llm


llm_provider_service = LLMProviderService()
