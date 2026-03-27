from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.ingestion import IngestRequest, IngestResponse
from app.services.ingestion_service import ingestion_service
import logging
import tempfile
import os
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.png', '.jpg', '.jpeg', '.webp', '.gif'}


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


@router.post("/upload", response_model=IngestResponse)
async def upload_file(
    file: UploadFile = File(...),
    metadata: str = Form(default="{}")
):
    """Upload and ingest a file (PDF, DOCX, TXT, MD, PNG, JPG, JPEG, WEBP, GIF)"""
    # Validate file extension
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Parse metadata JSON
    try:
        meta_dict = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")

    # Add filename to metadata
    meta_dict["filename"] = filename
    meta_dict["file_type"] = ext[1:]  # Remove the dot
    # Set title from original filename (without extension)
    title = os.path.splitext(filename)[0]
    meta_dict["title"] = title

    # Save to temp file and process
    tmp_path = None
    try:
        # Create temp file with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Processing uploaded file: {filename}")

        # Process using existing ingestion service
        result = await ingestion_service.ingest_file(tmp_path, meta_dict)

        return IngestResponse(**result)
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
