from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OrganizationBase(BaseModel):
    name: str
    website_domain: Optional[str] = None
    primary_color: str = "#6366f1"


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    website_domain: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    id: int
    slug: str
    owner_id: int
    logo_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Organization(OrganizationInDB):
    pass
