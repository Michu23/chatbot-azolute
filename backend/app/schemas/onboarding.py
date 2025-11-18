from pydantic import BaseModel
from typing import Optional, List
from app.models.bot import BotPersonality


class OnboardingStep1(BaseModel):
    """Step 1: Choose Bot Personality"""
    personality: BotPersonality
    custom_persona: Optional[str] = None


class OnboardingStep2(BaseModel):
    """Step 2: Basic Setup"""
    business_name: str
    website_domain: Optional[str] = None
    primary_color: str = "#6366f1"
    bot_name: str = "AI Assistant"
    welcome_message: str = "Hello! How can I help you today?"


class OnboardingStep3(BaseModel):
    """Step 3: Knowledge Upload"""
    urls: List[str] = []
    faqs: List[dict] = []  # [{"question": "...", "answer": "..."}]
    # PDFs handled separately via file upload


class OnboardingStep4(BaseModel):
    """Step 4: Complete - returns widget snippet"""
    pass


class OnboardingComplete(BaseModel):
    """Complete onboarding data"""
    step1: OnboardingStep1
    step2: OnboardingStep2
    step3: Optional[OnboardingStep3] = None


class OnboardingResponse(BaseModel):
    organization_id: int
    bot_id: str
    widget_script: str
    widget_iframe: str
