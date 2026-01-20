from fastapi import APIRouter, HTTPException
from app.models.document import DocumentListResponse, DeleteResponse
from app.services.qdrant_service import qdrant_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents():
    """Get all documents in the knowledge base"""
    try:
        documents = await qdrant_service.get_all_documents()
        return DocumentListResponse(documents=documents)
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str):
    """Delete a document and all its chunks from the knowledge base"""
    try:
        deleted_count = await qdrant_service.delete_document(document_id)
        return DeleteResponse(status="success", deleted_count=deleted_count)
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
