from typing import List
import re
from app.core.config import settings


class SemanticChunker:
    """Split text into semantic chunks with overlap for RAG"""

    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP

    def chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks with overlap"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings in reverse order
                for delimiter in ['. ', '! ', '? ', '.\n', '!\n', '?\n', '\n\n']:
                    last_pos = text.rfind(delimiter, start, end)
                    if last_pos != -1:
                        end = last_pos + len(delimiter)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.overlap

        return chunks
