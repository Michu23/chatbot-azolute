from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from app.core.database import Base
import enum


class SourceType(str, enum.Enum):
    URL = "url"
    PDF = "pdf"
    TEXT = "text"
    FAQ = "faq"


class IndexStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)

    source_type = Column(SQLEnum(SourceType), nullable=False)
    name = Column(String, nullable=False)

    # Source Details
    url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    content = Column(Text, nullable=True)

    # Status
    status = Column(SQLEnum(IndexStatus), default=IndexStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Metadata
    total_chunks = Column(Integer, default=0)
    last_crawled_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bot = relationship("Bot", back_populates="knowledge_sources")
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("knowledge_sources.id"), nullable=False)

    title = Column(String, nullable=True)
    url = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Metadata
    word_count = Column(Integer, default=0)
    metadata = Column(Text, nullable=True)  # JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source = relationship("KnowledgeSource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)

    # Vector embedding (1536 dimensions for OpenAI ada-002)
    embedding = Column(Vector(1536), nullable=True)

    # Metadata
    token_count = Column(Integer, default=0)
    metadata = Column(Text, nullable=True)  # JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="chunks")
