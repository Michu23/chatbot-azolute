from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any


class DashboardStats(BaseModel):
    total_conversations: int
    total_users: int
    total_messages: int
    leads_collected: int
    avg_response_time_ms: float
    model_usage: Dict[str, int]


class ConversationTrend(BaseModel):
    date: str
    count: int


class DashboardAnalytics(BaseModel):
    stats: DashboardStats
    conversation_trends: List[ConversationTrend]
    top_pages: List[Dict[str, Any]]
    recent_leads: int
