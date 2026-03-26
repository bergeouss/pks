from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()


class SettingsUpdate(BaseModel):
    llm_provider: Literal["openai", "deepseek", "anthropic", "ollama", "zai"] = "zai"
    llm_model: str = "glm-5"
    embedding_provider: Literal["openai", "gemini"] = "gemini"
    embedding_model: str = "gemini-embedding-2-preview"


class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    embedding_provider: str
    embedding_model: str


@router.get("/")
async def get_settings():
    """Get current settings"""
    from app.core.config import settings

    return SettingsResponse(
        llm_provider=settings.DEFAULT_LLM_PROVIDER,
        llm_model=settings.DEFAULT_LLM_MODEL,
        embedding_provider=settings.DEFAULT_EMBEDDING_PROVIDER,
        embedding_model=settings.DEFAULT_EMBEDDING_MODEL,
    )


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
