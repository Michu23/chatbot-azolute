from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from app.models.knowledge import SourceType, IndexStatus


class KnowledgeSourceBase(BaseModel):
    source_type: SourceType
    name: str


class KnowledgeSourceCreate(KnowledgeSourceBase):
    bot_id: int
    url: Optional[str] = None
    content: Optional[str] = None


class KnowledgeSourceUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


class KnowledgeSourceInDB(KnowledgeSourceBase):
    id: int
    bot_id: int
    url: Optional[str]
    file_path: Optional[str]
    content: Optional[str]
    status: IndexStatus
    error_message: Optional[str]
    total_chunks: int
    last_crawled_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class KnowledgeSource(KnowledgeSourceInDB):
    pass


class KnowledgeSourceList(BaseModel):
    sources: List[KnowledgeSource]
    total: int


class DocumentChunkResponse(BaseModel):
    content: str
    metadata: Optional[str]
    score: float
