from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    # Contact Info
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    message = Column(Text, nullable=True)

    # Additional Data
    tags = Column(Text, nullable=True)  # JSON array
    custom_fields = Column(Text, nullable=True)  # JSON object

    # Source
    source_url = Column(String, nullable=True)
    source_page = Column(String, nullable=True)
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)

    # Status
    is_qualified = Column(Boolean, default=False)
    is_contacted = Column(Boolean, default=False)
    webhook_sent = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="lead")
