from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class IngestRequest(BaseModel):
    url: Optional[str] = Field(None, description="URL to ingest")
    text: Optional[str] = Field(None, description="Raw text to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class IngestResponse(BaseModel):
    document_id: str
    chunks_count: int
    point_ids: list[str]
    status: str
