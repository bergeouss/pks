from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import ingestion, chat, documents, health, settings as settings_route

setup_logging()

app = FastAPI(
    title="Personal Knowledge Synthesizer API",
    version="1.0.0",
    description="Self-hosted knowledge management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Self-hosted; no cookies/credentials used by the SPA
    allow_credentials=False,  # credentials=True + origin "*" is rejected by browsers
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(settings_route.router, prefix="/api/v1/settings", tags=["settings"])


@app.on_event("startup")
async def startup_event():
    """Initialize Qdrant collection on startup"""
    from app.services.qdrant_service import qdrant_service
    from app.services.embedding_service import embedding_vector_size
    from app.core.runtime_settings import get_runtime_settings

    rt = get_runtime_settings()
    vector_size = embedding_vector_size(rt["embedding_provider"], rt["embedding_model"])
    await qdrant_service.initialize_collection(vector_size=vector_size)


@app.get("/")
async def root():
    return {"message": "PKS API is running", "version": "1.0.0"}

