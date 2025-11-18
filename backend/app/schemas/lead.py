from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None


class LeadCreate(LeadBase):
    session_id: str


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None
    tags: Optional[str] = None
    is_qualified: Optional[bool] = None
    is_contacted: Optional[bool] = None


class LeadInDB(LeadBase):
    id: int
    session_id: int
    tags: Optional[str]
    custom_fields: Optional[str]
    source_url: Optional[str]
    source_page: Optional[str]
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    is_qualified: bool
    is_contacted: bool
    webhook_sent: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Lead(LeadInDB):
    pass


class LeadList(BaseModel):
    leads: List[Lead]
    total: int
