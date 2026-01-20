from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User query")
    history: Optional[List[ChatMessage]] = Field(None, description="Conversation history")


class SourceInfo(BaseModel):
    title: str
    url: str
    source: str


class ChatResponse(BaseModel):
    response: str
    sources: List[SourceInfo]
    context_used: int
