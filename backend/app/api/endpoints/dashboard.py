from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.bot import Bot
from app.models.chat import ChatSession, ChatMessage
from app.models.lead import Lead
from app.schemas.dashboard import DashboardStats, DashboardAnalytics, ConversationTrend

router = APIRouter()


@router.get("/stats", response_model=DashboardAnalytics)
async def get_dashboard_stats(
    days: int = 7,
    bot_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard analytics and stats"""
    # Base query for user's organizations
    org_query = select(Organization.id).where(Organization.owner_id == current_user.id)
    org_result = await db.execute(org_query)
    org_ids = [row[0] for row in org_result.fetchall()]

    if not org_ids:
        return DashboardAnalytics(
            stats=DashboardStats(
                total_conversations=0,
                total_users=0,
                total_messages=0,
                leads_collected=0,
                avg_response_time_ms=0,
                model_usage={},
            ),
            conversation_trends=[],
            top_pages=[],
            recent_leads=0,
        )

    # Get bot IDs
    bot_query = select(Bot.id).where(Bot.organization_id.in_(org_ids))
    if bot_id:
        bot_query = bot_query.where(Bot.bot_id == bot_id)
    bot_result = await db.execute(bot_query)
    bot_ids = [row[0] for row in bot_result.fetchall()]

    # Total conversations
    conv_result = await db.execute(
        select(func.count(ChatSession.id)).where(ChatSession.bot_id.in_(bot_ids))
    )
    total_conversations = conv_result.scalar() or 0

    # Total unique users (visitors)
    users_result = await db.execute(
        select(func.count(func.distinct(ChatSession.visitor_id)))
        .where(ChatSession.bot_id.in_(bot_ids))
    )
    total_users = users_result.scalar() or 0

    # Total messages
    msg_result = await db.execute(
        select(func.count(ChatMessage.id))
        .join(ChatSession)
        .where(ChatSession.bot_id.in_(bot_ids))
    )
    total_messages = msg_result.scalar() or 0

    # Total leads
    leads_result = await db.execute(
        select(func.count(Lead.id))
        .join(ChatSession)
        .where(ChatSession.bot_id.in_(bot_ids))
    )
    leads_collected = leads_result.scalar() or 0

    # Average response time
    avg_time_result = await db.execute(
        select(func.avg(ChatMessage.response_time_ms))
        .join(ChatSession)
        .where(
            ChatSession.bot_id.in_(bot_ids),
            ChatMessage.response_time_ms.isnot(None)
        )
    )
    avg_response_time_ms = avg_time_result.scalar() or 0

    # Model usage
    model_result = await db.execute(
        select(
            ChatMessage.model_used,
            func.count(ChatMessage.id)
        )
        .join(ChatSession)
        .where(
            ChatSession.bot_id.in_(bot_ids),
            ChatMessage.model_used.isnot(None)
        )
        .group_by(ChatMessage.model_used)
    )
    model_usage = {row[0]: row[1] for row in model_result.fetchall()}

    # Conversation trends (last N days)
    start_date = datetime.utcnow() - timedelta(days=days)
    trends = []

    for i in range(days):
        day = start_date + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        count_result = await db.execute(
            select(func.count(ChatSession.id))
            .where(
                ChatSession.bot_id.in_(bot_ids),
                ChatSession.created_at >= day_start,
                ChatSession.created_at < day_end
            )
        )
        count = count_result.scalar() or 0

        trends.append(ConversationTrend(
            date=day.strftime('%Y-%m-%d'),
            count=count
        ))

    # Top pages
    pages_result = await db.execute(
        select(
            ChatSession.source_url,
            func.count(ChatSession.id).label('count')
        )
        .where(
            ChatSession.bot_id.in_(bot_ids),
            ChatSession.source_url.isnot(None)
        )
        .group_by(ChatSession.source_url)
        .order_by(desc('count'))
        .limit(5)
    )
    top_pages = [
        {"url": row[0], "count": row[1]}
        for row in pages_result.fetchall()
    ]

    # Recent leads (last 7 days)
    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_leads_result = await db.execute(
        select(func.count(Lead.id))
        .join(ChatSession)
        .where(
            ChatSession.bot_id.in_(bot_ids),
            Lead.created_at >= recent_date
        )
    )
    recent_leads = recent_leads_result.scalar() or 0

    return DashboardAnalytics(
        stats=DashboardStats(
            total_conversations=total_conversations,
            total_users=total_users,
            total_messages=total_messages,
            leads_collected=leads_collected,
            avg_response_time_ms=float(avg_response_time_ms),
            model_usage=model_usage,
        ),
        conversation_trends=trends,
        top_pages=top_pages,
        recent_leads=recent_leads,
    )
