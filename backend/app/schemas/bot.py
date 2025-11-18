from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.bot import BotPersonality, BotPosition, BotVisibility


class BotBase(BaseModel):
    name: str
    personality: BotPersonality = BotPersonality.FRIENDLY
    custom_persona: Optional[str] = None
    welcome_message: str = "Hello! How can I help you today?"
    offline_message: str = "We're currently offline. Please leave a message."


class BotCreate(BotBase):
    organization_id: int


class BotUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[BotPersonality] = None
    custom_persona: Optional[str] = None
    welcome_message: Optional[str] = None
    offline_message: Optional[str] = None
    primary_color: Optional[str] = None
    button_color: Optional[str] = None
    chat_bubble_color: Optional[str] = None
    theme_mode: Optional[str] = None
    profile_image_url: Optional[str] = None
    position: Optional[BotPosition] = None
    visibility: Optional[BotVisibility] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    lead_capture_enabled: Optional[bool] = None
    quick_suggestions_enabled: Optional[bool] = None
    quick_suggestions: Optional[str] = None
    n8n_webhook_url: Optional[str] = None
    send_lead_webhook: Optional[bool] = None
    is_online: Optional[bool] = None


class BotInDB(BotBase):
    id: int
    bot_id: str
    organization_id: int
    primary_color: str
    button_color: str
    chat_bubble_color: str
    theme_mode: str
    profile_image_url: Optional[str]
    position: BotPosition
    visibility: BotVisibility
    model_name: str
    temperature: float
    max_tokens: int
    system_prompt: Optional[str]
    lead_capture_enabled: bool
    quick_suggestions_enabled: bool
    quick_suggestions: Optional[str]
    n8n_webhook_url: Optional[str]
    send_lead_webhook: bool
    is_active: bool
    is_online: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Bot(BotInDB):
    pass


class BotList(BaseModel):
    bots: List[Bot]
    total: int
