"""Runtime settings override layer.

Env vars (app.core.config.settings) are frozen at process start. This module
layers a writable JSON file (data/settings.json, inside the mounted data
volume) on top of them so the Settings UI can change provider/model without a
backend restart.

Merge order: runtime override > env default.
"""
import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict

from app.core.config import settings as env_settings

# Resolves to /app/data/settings.json in Docker (./data is mounted at /app/data)
# and ./data/settings.json in local dev.
RUNTIME_PATH = Path("data/settings.json")
_lock = Lock()

_OVERRIDE_KEYS = ("llm_provider", "llm_model", "embedding_provider", "embedding_model")


def _read_overrides() -> Dict[str, Any]:
    try:
        if RUNTIME_PATH.exists():
            data = json.loads(RUNTIME_PATH.read_text())
            if isinstance(data, dict):
                return {k: v for k, v in data.items() if k in _OVERRIDE_KEYS}
    except Exception:
        pass
    return {}


def get_runtime_settings() -> Dict[str, str]:
    """Return effective settings: runtime override merged on top of env defaults."""
    o = _read_overrides()
    return {
        "llm_provider": o.get("llm_provider") or env_settings.DEFAULT_LLM_PROVIDER,
        "llm_model": o.get("llm_model") or env_settings.DEFAULT_LLM_MODEL,
        "embedding_provider": o.get("embedding_provider") or env_settings.DEFAULT_EMBEDDING_PROVIDER,
        "embedding_model": o.get("embedding_model") or env_settings.DEFAULT_EMBEDDING_MODEL,
    }


def save_runtime_settings(
    llm_provider: str,
    llm_model: str,
    embedding_provider: str,
    embedding_model: str,
) -> Dict[str, str]:
    """Persist the four selectable fields. No restart required."""
    data = {
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
    }
    with _lock:
        RUNTIME_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME_PATH.write_text(json.dumps(data, indent=2))
    return data