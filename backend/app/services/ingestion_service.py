from app.core.chunking import SemanticChunker
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.youtube_service import youtube_service
from app.services.parser_service import parser_service
from typing import Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class IngestionService:
    """Core ingestion pipeline for processing and storing knowledge"""

    def __init__(self):
        self.chunker = SemanticChunker()

    async def ingest_url(self, url: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest content from a URL"""
        metadata = metadata or {}

        # Check if YouTube
        if "youtube.com" in url or "youtu.be" in url:
            text = await youtube_service.get_transcript(url)
            metadata["source"] = "youtube"
            metadata["title"] = f"YouTube: {url.split('=')[-1]}" if "v=" in url else "YouTube Video"
        else:
            text, title = await parser_service.fetch_webpage(url)
            metadata["source"] = "web"
            metadata["title"] = title

        metadata["url"] = url
        return await self._process_text(text, metadata)

    async def ingest_file(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest content from a file"""
        metadata = metadata or {}
        text = await parser_service.parse_file(file_path)
        metadata["source"] = "file"
        metadata["filename"] = file_path
        # Use filename as title (without extension)
        import os
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        # Only set title if not already in metadata
        if "title" not in metadata:
            metadata["title"] = title

        return await self._process_text(text, metadata)

    async def ingest_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest raw text"""
        metadata = metadata or {}
        metadata["source"] = "direct"
        # Set default title for direct text if not provided
        if "title" not in metadata:
            # Use first 100 chars as title
            metadata["title"] = text[:100].replace('\n', ' ')[:50] + "..."
        return await self._process_text(text, metadata)

    async def _process_text(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text through chunking, embedding, and storage"""
        document_id = metadata.get("document_id") or str(uuid.uuid4())
        metadata["document_id"] = document_id

        # Chunk text
        chunks = self.chunker.chunk(text)
        logger.info(f"Chunked text into {len(chunks)} chunks")

        # Generate embeddings
        embeddings = await embedding_service.embed_texts(chunks)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Prepare chunks for Qdrant
        chunk_data = [
            {
                "text": chunk,
                "embedding": emb,
                **metadata,
            }
            for chunk, emb in zip(chunks, embeddings)
        ]

        # Store in Qdrant
        point_ids = await qdrant_service.upsert_chunks(chunk_data)
        logger.info(f"Stored {len(point_ids)} chunks in Qdrant")

        # Return metadata in response
        result = {
            "document_id": document_id,
            "chunks_count": len(chunks),
            "point_ids": point_ids,
            "status": "success",
        }
        # Add metadata fields
        for key in ["title", "source", "url", "filename"]:
            if key in metadata:
                result[key] = metadata[key]

        return result


ingestion_service = IngestionService()
