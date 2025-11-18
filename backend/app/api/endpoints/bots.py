from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from app.schemas.bot import Bot as BotSchema, BotUpdate, BotList

router = APIRouter()


async def get_user_bot(bot_id: str, user_id: int, db: AsyncSession) -> Bot:
    """Get bot that belongs to user's organization"""
    result = await db.execute(
        select(Bot)
        .join(Organization)
        .where(
            Bot.bot_id == bot_id,
            Organization.owner_id == user_id
        )
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@router.get("/", response_model=BotList)
async def list_bots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all bots for user's organizations"""
    result = await db.execute(
        select(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
    )
    bots = result.scalars().all()
    return BotList(bots=bots, total=len(bots))


@router.get("/{bot_id}", response_model=BotSchema)
async def get_bot(
    bot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get bot by ID"""
    bot = await get_user_bot(bot_id, current_user.id, db)
    return bot


@router.patch("/{bot_id}", response_model=BotSchema)
async def update_bot(
    bot_id: str,
    bot_update: BotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update bot configuration"""
    bot = await get_user_bot(bot_id, current_user.id, db)

    # Update all provided fields
    update_data = bot_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)

    await db.commit()
    await db.refresh(bot)
    return bot


@router.get("/{bot_id}/widget-code")
async def get_widget_code(
    bot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get widget embedding code"""
    bot = await get_user_bot(bot_id, current_user.id, db)

    from app.core.config import settings

    widget_script = f'''<!-- Azolute AI Chatbot -->
<script src="{settings.FRONTEND_URL}/widget.js" data-bot-id="{bot.bot_id}"></script>'''

    widget_iframe = f'''<!-- Azolute AI Chatbot (iframe version) -->
<iframe
    src="{settings.FRONTEND_URL}/widget?bot={bot.bot_id}"
    style="position:fixed;bottom:20px;right:20px;width:400px;height:600px;border:none;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.15);"
    allow="clipboard-read; clipboard-write"
></iframe>'''

    return {
        "bot_id": bot.bot_id,
        "widget_script": widget_script,
        "widget_iframe": widget_iframe,
    }
