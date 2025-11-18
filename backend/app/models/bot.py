from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BotPersonality(str, enum.Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    SALES_FOCUSED = "sales_focused"
    CUSTOM = "custom"


class BotPosition(str, enum.Enum):
    LEFT = "left"
    RIGHT = "right"


class BotVisibility(str, enum.Enum):
    BOTH = "both"
    MOBILE = "mobile"
    DESKTOP = "desktop"


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Basic Info
    name = Column(String, default="AI Assistant")
    bot_id = Column(String, unique=True, index=True, nullable=False)  # Public ID for widget

    # Personality & Behavior
    personality = Column(SQLEnum(BotPersonality), default=BotPersonality.FRIENDLY)
    custom_persona = Column(Text, nullable=True)
    welcome_message = Column(Text, default="Hello! How can I help you today?")
    offline_message = Column(Text, default="We're currently offline. Please leave a message.")

    # Appearance
    primary_color = Column(String, default="#6366f1")
    button_color = Column(String, default="#6366f1")
    chat_bubble_color = Column(String, default="#ffffff")
    theme_mode = Column(String, default="light")  # light, dark, auto
    profile_image_url = Column(String, nullable=True)
    position = Column(SQLEnum(BotPosition), default=BotPosition.RIGHT)
    visibility = Column(SQLEnum(BotVisibility), default=BotVisibility.BOTH)

    # AI Configuration
    model_name = Column(String, default="gpt-3.5-turbo")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=500)
    system_prompt = Column(Text, nullable=True)

    # Features
    lead_capture_enabled = Column(Boolean, default=True)
    quick_suggestions_enabled = Column(Boolean, default=True)
    quick_suggestions = Column(Text, nullable=True)  # JSON array of suggestions

    # Webhooks
    n8n_webhook_url = Column(String, nullable=True)
    send_lead_webhook = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="bots")
    chat_sessions = relationship("ChatSession", back_populates="bot", cascade="all, delete-orphan")
    knowledge_sources = relationship("KnowledgeSource", back_populates="bot", cascade="all, delete-orphan")
