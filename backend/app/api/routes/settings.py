from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()


class SettingsUpdate(BaseModel):
    llm_provider: Literal["openai", "deepseek", "anthropic", "ollama", "zai"] = "zai"
    llm_model: str = "glm-5"
    embedding_provider: Literal["openai", "gemini", "ollama"] = "gemini"
    embedding_model: str = "gemini-embedding-2-preview"


class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    embedding_provider: str
    embedding_model: str


@router.get("/v1", response_model=SettingsResponse)
async def get_settings():
    """Get current settings"""
    from app.core.config import settings

    return SettingsResponse(
        llm_provider=settings.DEFAULT_LLM_PROVIDER,
        llm_model=settings.DEFAULT_LLM_MODEL or "glm-5",
        embedding_provider=settings.DEFAULT_EMBEDDING_PROVIDER,
        embedding_model=settings.DEFAULT_EMBEDDING_MODEL or "gemini-embedding-2-preview",
    )


@router.get("/v1/llm-models")
async def get_llm_models():
    """Get available LLM models for ALL providers"""
    from app.core.config import settings
    import logging
    import requests as req

    logger = logging.getLogger(__name__)
    models = {}

    # Fetch OpenAI models
    try:
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.models.list()
            models["openai"] = sorted([m.id for m in response.data if "gpt" in m.id.lower()])
            logger.info(f"Fetched OpenAI models: {len(models['openai'])} models")
    except Exception as e:
        logger.warning(f"Could not fetch OpenAI models: {e}")
        models["openai"] = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    # DeepSeek models (hardcoded - no public models API)
    models["deepseek"] = ["deepseek-chat", "deepseek-coder"]

    # Anthropic models (hardcoded - no public models API)
    models["anthropic"] = [
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    # Ollama models - fetch from local API
    try:
        ollama_url = settings.OLLAMA_BASE_URL or "http://host.docker.internal:11434"
        response = req.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models["ollama"] = [model["name"] for model in data.get("models", [])]
            logger.info(f"Fetched Ollama models: {models['ollama']}")
        else:
            models["ollama"] = []
    except Exception as e:
        logger.warning(f"Could not fetch Ollama models: {e}")
        models["ollama"] = []

    # Z.ai models - fetch from API
    try:
        if settings.ZAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(
                api_key=settings.ZAI_API_KEY,
                base_url=settings.ZAI_BASE_URL
            )
            response = client.models.list()
            models["zai"] = sorted([model.id for model in response.data if model.id.startswith("glm")])
            logger.info(f"Fetched Z.ai models: {models['zai']}")
    except Exception as e:
        logger.warning(f"Could not fetch Z.ai models: {e}")
        models["zai"] = ["glm-5", "glm-4", "glm-4-plus", "glm-4-air"]

    logger.info(f"Returning models for all providers: {list(models.keys())}")
    return {"models": models}


@router.get("/v1/embedding-models")
async def get_embedding_models():
    """Get available embedding models for ALL providers"""
    from app.core.config import settings
    import logging
    import requests as req

    logger = logging.getLogger(__name__)
    models = {}

    # OpenAI embedding models
    try:
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.models.list()
            models["openai"] = sorted([m.id for m in response.data if "embedding" in m.id.lower()])
            if not models["openai"]:
                models["openai"] = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
            logger.info(f"Fetched OpenAI embedding models: {len(models['openai'])} models")
    except Exception as e:
        logger.warning(f"Could not fetch OpenAI embedding models: {e}")
        models["openai"] = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]

    # Gemini embedding models (hardcoded - no public models API for embeddings)
    models["gemini"] = ["gemini-embedding-2-preview", "gemini-embedding-001"]

    # Ollama embedding models - fetch from local API and filter for embedding-capable models
    try:
        ollama_url = settings.OLLAMA_BASE_URL or "http://host.docker.internal:11434"
        response = req.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Common embedding models in Ollama
            embedding_keywords = ["embed", "nomic", "mxbai", "bge", "e5"]
            all_models = [model["name"] for model in data.get("models", [])]
            models["ollama"] = [m for m in all_models if any(kw in m.lower() for kw in embedding_keywords)]
            if not models["ollama"]:
                # If no embedding models found, show all models (user can use any for local embeddings)
                models["ollama"] = all_models[:5]  # Limit to first 5
            logger.info(f"Fetched Ollama embedding models: {models['ollama']}")
    except Exception as e:
        logger.warning(f"Could not fetch Ollama embedding models: {e}")
        models["ollama"] = ["nomic-embed-text", "mxbai-embed-large", "bge-m3"]

    logger.info(f"Returning embedding models for all providers: {list(models.keys())}")
    return {"models": models}


@router.post("/")
async def update_settings(update: SettingsUpdate):
    """Update settings (for testing - normally via .env file)"""
    from app.core.config import settings
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Updating settings: {update.model_dump()}")

    # Note: For production, settings should be changed via environment variables
    # This endpoint allows testing configuration changes without restart
    logger.warning(
        "Settings changes require backend restart. "
        f"Update .env file with: DEFAULT_LLM_PROVIDER={update.llm_provider}, "
        f"DEFAULT_LLM_MODEL={update.llm_model}, "
        f"DEFAULT_EMBEDDING_PROVIDER={update.embedding_provider}, "
        f"DEFAULT_EMBEDDING_MODEL={update.embedding_model}"
    )

    return {
        "message": "Settings updated. Backend restart required for changes to take effect.",
        "settings": update.model_dump(),
    }
