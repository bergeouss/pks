from fastapi import APIRouter
from app.services.qdrant_service import qdrant_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = qdrant_service._get_client()
        collections = client.get_collections()
        qdrant_connected = len(collections.collections) >= 0

        return {
            "status": "healthy",
            "qdrant_connected": qdrant_connected,
            "collection_name": qdrant_service.collection_name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "qdrant_connected": False,
            "error": str(e),
        }
