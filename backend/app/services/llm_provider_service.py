from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.core.config import settings
from app.core.runtime_settings import get_runtime_settings
import logging

logger = logging.getLogger(__name__)


class LLMProviderService:
    """Multi-provider LLM service using LangChain.

    Reads the active provider/model from the runtime override layer so the
    Settings UI can switch models without a backend restart.
    """

    def __init__(self):
        self._cache_key = None
        self._llm = None

    def get_llm(self, provider: str = None, model: str = None):
        """Get LLM instance for specified provider/model (defaults to runtime settings)."""
        rt = get_runtime_settings()
        provider = provider or rt["llm_provider"]
        model = model or rt["llm_model"]
        cache_key = (provider, model)

        # Return cached LLM if provider+model hasn't changed
        if self._cache_key == cache_key and self._llm:
            return self._llm

        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or settings.DEFAULT_LLM_MODEL,
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
            if not settings.OLLAMA_BASE_URL:
                raise ValueError("OLLAMA_BASE_URL not configured")
            # Ollama exposes an OpenAI-compatible API under /v1
            base = settings.OLLAMA_BASE_URL.rstrip("/")
            if not base.endswith("/v1"):
                base += "/v1"
            self._llm = ChatOpenAI(
                model=model or "llama3",
                base_url=base,
                temperature=0.7,
            )
        elif provider == "zai":
            if not settings.ZAI_API_KEY:
                raise ValueError("ZAI_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or "glm-5",
                openai_api_key=settings.ZAI_API_KEY,
                base_url=settings.ZAI_BASE_URL,
                temperature=0.7,
            )
        elif provider == "opencodego":
            if not settings.OPENCODEGO_API_KEY:
                raise ValueError("OPENCODEGO_API_KEY not configured")
            self._llm = ChatOpenAI(
                model=model or "deepseek-v4-flash",
                openai_api_key=settings.OPENCODEGO_API_KEY,
                base_url=settings.OPENCODEGO_BASE_URL,
                temperature=0.7,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        self._cache_key = cache_key
        logger.info(f"Initialized LLM with provider: {provider}, model: {model}")
        return self._llm


llm_provider_service = LLMProviderService()