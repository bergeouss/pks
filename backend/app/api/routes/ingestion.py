from fastapi import APIRouter, HTTPException
from app.models.ingestion import IngestRequest, IngestResponse
from app.services.ingestion_service import ingestion_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_content(request: IngestRequest):
    """Ingest content from URL, file, or direct text"""
    try:
        if request.url:
            result = await ingestion_service.ingest_url(request.url, request.metadata or {})
        elif request.text:
            result = await ingestion_service.ingest_text(request.text, request.metadata or {})
        else:
            raise HTTPException(status_code=400, detail="Either 'url' or 'text' must be provided")

        return IngestResponse(**result)
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
