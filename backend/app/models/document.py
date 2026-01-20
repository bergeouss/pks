from pydantic import BaseModel
from typing import Optional


class DocumentInfo(BaseModel):
    id: str
    title: str
    url: Optional[str] = ""
    source: str
    timestamp: Optional[str] = ""


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]


class DeleteResponse(BaseModel):
    status: str
    deleted_count: int
