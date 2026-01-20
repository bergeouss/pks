from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import ingestion, chat, documents, health

setup_logging()

app = FastAPI(
    title="Personal Knowledge Synthesizer API",
    version="1.0.0",
    description="Self-hosted knowledge management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Initialize Qdrant collection on startup"""
    from app.services.qdrant_service import qdrant_service
    from app.core.config import settings

    # Determine vector size based on embedding provider
    # Gemini: 768, OpenAI: 1536
    vector_size = 768 if settings.DEFAULT_EMBEDDING_PROVIDER == "gemini" else 1536
    await qdrant_service.initialize_collection(vector_size=vector_size)


@app.get("/")
async def root():
    return {"message": "PKS API is running", "version": "1.0.0"}

