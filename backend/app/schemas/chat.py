from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.chat import MessageRole, SessionStatus


class ChatMessageBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    role: MessageRole
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: str


class ChatMessageInDB(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: int
    session_id: int
    token_count: Optional[int]
    model_used: Optional[str]
    response_time_ms: Optional[int]
    used_rag: bool
    source_documents: Optional[str]
    created_at: datetime


class ChatMessage(ChatMessageInDB):
    pass


class ChatSessionBase(BaseModel):
    bot_id: str
    source_url: Optional[str] = None
    source_page_title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    visitor_id: Optional[str] = None


class ChatSessionUpdate(BaseModel):
    visitor_name: Optional[str] = None
    visitor_email: Optional[str] = None
    visitor_phone: Optional[str] = None
    status: Optional[SessionStatus] = None


class ChatSessionInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: str
    bot_id: int
    visitor_id: Optional[str]
    visitor_name: Optional[str]
    visitor_email: Optional[str]
    visitor_phone: Optional[str]
    source_url: Optional[str]
    source_page_title: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
    status: SessionStatus
    is_lead: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_message_at: Optional[datetime]


class ChatSession(ChatSessionInDB):
    messages: List[ChatMessage] = []


class ChatSessionWithMessages(ChatSession):
    pass


class ChatRequest(BaseModel):
    session_id: str
    message: str
    visitor_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage
    bot_response: str
