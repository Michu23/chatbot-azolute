from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)

    # Visitor Info
    visitor_id = Column(String, nullable=True)
    visitor_name = Column(String, nullable=True)
    visitor_email = Column(String, nullable=True)
    visitor_phone = Column(String, nullable=True)

    # Metadata
    source_url = Column(String, nullable=True)
    source_page_title = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)

    # Status
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    is_lead = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    bot = relationship("Bot", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    lead = relationship("Lead", back_populates="session", uselist=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Metadata
    token_count = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    response_time_ms = Column(Integer, nullable=True)

    # RAG Context
    used_rag = Column(Boolean, default=False)
    source_documents = Column(Text, nullable=True)  # JSON array of source doc IDs

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
