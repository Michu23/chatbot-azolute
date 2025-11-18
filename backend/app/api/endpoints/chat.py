from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
import secrets

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.chat import ChatSession, ChatMessage, MessageRole, SessionStatus
from app.models.organization import Organization
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSession as ChatSessionSchema,
    ChatMessage as ChatMessageSchema,
    ChatRequest,
    ChatResponse,
    ChatSessionUpdate,
)

router = APIRouter()


@router.post("/session", response_model=ChatSessionSchema)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session (public endpoint for widget)"""
    # Get bot
    result = await db.execute(select(Bot).where(Bot.bot_id == session_data.bot_id))
    bot = result.scalar_one_or_none()
    if not bot or not bot.is_active:
        raise HTTPException(status_code=404, detail="Bot not found or inactive")

    # Create session
    session_id = secrets.token_urlsafe(32)
    session = ChatSession(
        session_id=session_id,
        bot_id=bot.id,
        visitor_id=session_data.visitor_id,
        source_url=session_data.source_url,
        source_page_title=session_data.source_page_title,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get bot response (public endpoint for widget)"""
    # Get session
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == message_data.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get bot
    result = await db.execute(select(Bot).where(Bot.id == session.bot_id))
    bot = result.scalar_one_or_none()

    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=message_data.message,
    )
    db.add(user_message)

    # Generate bot response (simplified - would use RAG/OpenAI in production)
    # For now, a simple response
    bot_response_text = f"Thank you for your message! I'm {bot.name}. How can I help you today?"

    # Save bot response
    bot_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=bot_response_text,
        model_used=bot.model_name,
    )
    db.add(bot_message)

    # Update session
    session.last_message_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user_message)

    return ChatResponse(
        session_id=session.session_id,
        message=user_message,
        bot_response=bot_response_text,
    )


@router.get("/sessions", response_model=list[ChatSessionSchema])
async def list_sessions(
    bot_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List chat sessions for user's bots"""
    query = (
        select(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
        .order_by(desc(ChatSession.last_message_at))
    )

    if bot_id:
        query = query.where(Bot.bot_id == bot_id)

    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat session with messages"""
    result = await db.execute(
        select(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(
            ChatSession.session_id == session_id,
            Organization.owner_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Load messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    session.messages = messages

    return session


@router.patch("/sessions/{session_id}", response_model=ChatSessionSchema)
async def update_session(
    session_id: str,
    session_update: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update chat session (mark lead, resolve, etc)"""
    result = await db.execute(
        select(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(
            ChatSession.session_id == session_id,
            Organization.owner_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update fields
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)
    return session
