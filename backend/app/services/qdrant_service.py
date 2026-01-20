from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    """Vector database operations using Qdrant"""

    def __init__(self):
        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def _get_client(self) -> QdrantClient:
        """Lazy initialization of Qdrant client"""
        if self.client is None:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
        return self.client

    async def initialize_collection(self, vector_size: int = 768):
        """Create collection if it doesn't exist"""
        client = self._get_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Created collection: {self.collection_name} with vector size {vector_size}")
        else:
            # Get existing collection info to check vector size
            collection_info = client.get_collection(self.collection_name)
            existing_size = collection_info.config.params.vectors.size
            logger.info(f"Collection already exists: {self.collection_name} with vector size {existing_size}")

            if existing_size != vector_size:
                logger.warning(
                    f"Vector size mismatch! Requested {vector_size} but collection has {existing_size}. "
                    f"Delete and recreate collection to change embedding model."
                )

    async def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Insert text chunks with embeddings into Qdrant"""
        client = self._get_client()
        points = []
        point_ids = []

        for chunk in chunks:
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            points.append(
                PointStruct(
                    id=point_id,
                    vector=chunk["embedding"],
                    payload={
                        "text": chunk["text"],
                        "source": chunk.get("source", ""),
                        "title": chunk.get("title", ""),
                        "url": chunk.get("url", ""),
                        "author": chunk.get("author", ""),
                        "timestamp": chunk.get("timestamp", ""),
                        "document_id": chunk.get("document_id", ""),
                    },
                )
            )

        client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(f"Upserted {len(points)} chunks to Qdrant")
        return point_ids

    async def search(self, query_vector: List[float], limit: int = None) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        client = self._get_client()
        limit = limit or settings.TOP_K_RESULTS

        results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "text": r.payload.get("text", ""),
                "source": r.payload.get("source", ""),
                "title": r.payload.get("title", ""),
                "url": r.payload.get("url", ""),
                "document_id": r.payload.get("document_id", ""),
            }
            for r in results
        ]

    async def delete_document(self, document_id: str) -> int:
        """Delete all chunks associated with a document"""
        client = self._get_client()
        # First count how many points will be deleted
        count_result = client.count(
            collection_name=self.collection_name,
            count_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        deleted_count = count_result.count

        # Then delete the points
        client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        logger.info(f"Deleted document {document_id} with {deleted_count} chunks")
        return deleted_count

    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all unique documents from the collection"""
        client = self._get_client()
        # Scroll through all points and extract unique document_ids
        documents = {}
        offset = None

        while True:
            records, offset = client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
            )

            for record in records:
                doc_id = record.payload.get("document_id")
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "title": record.payload.get("title", ""),
                        "url": record.payload.get("url", ""),
                        "source": record.payload.get("source", ""),
                        "timestamp": record.payload.get("timestamp", ""),
                    }

            if offset is None:
                break

        return list(documents.values())


qdrant_service = QdrantService()
