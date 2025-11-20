from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import secrets
import time

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
from app.services.ai import generate_rag_response, generate_chat_response
from app.services.cache import cache_get, cache_set, cache_delete
from app.services.webhook import send_conversation_to_n8n

router = APIRouter()


@router.post("/session", response_model=ChatSessionSchema)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session (public endpoint for widget) - Optimized"""

    # Try cache first for bot data
    cache_key = f"bot:{session_data.bot_id}"
    bot_data = await cache_get(cache_key)

    if not bot_data:
        # Get bot from database with minimal fields
        result = await db.execute(
            select(Bot.id, Bot.name, Bot.is_active, Bot.is_online)
            .where(Bot.bot_id == session_data.bot_id)
        )
        bot_row = result.first()

        if not bot_row or not bot_row.is_active:
            raise HTTPException(status_code=404, detail="Bot not found or inactive")

        bot_id = bot_row.id

        # Cache bot data for 5 minutes
        await cache_set(cache_key, {"id": bot_id, "active": bot_row.is_active}, expire=300)
    else:
        bot_id = bot_data["id"]
        if not bot_data.get("active"):
            raise HTTPException(status_code=404, detail="Bot not found or inactive")

    # Create session with optimized insert
    session_id = secrets.token_urlsafe(32)
    session = ChatSession(
        session_id=session_id,
        bot_id=bot_id,
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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get bot response (optimized with AI)"""
    start_time = time.time()

    # Get session with bot data in single query
    result = await db.execute(
        select(ChatSession, Bot)
        .join(Bot, ChatSession.bot_id == Bot.id)
        .where(ChatSession.session_id == message_data.session_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    session, bot = row

    # Get recent conversation context (last 10 messages)
    context_result = await db.execute(
        select(ChatMessage.role, ChatMessage.content)
        .where(ChatMessage.session_id == session.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(10)
    )
    context_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in reversed(context_result.scalars().all())
    ]

    # Save user message immediately
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=message_data.message,
    )
    db.add(user_message)
    await db.flush()

    # Generate AI response with RAG
    try:
        bot_response_text, source_docs = await generate_rag_response(
            message=message_data.message,
            bot_id=bot.id,
            bot_name=bot.name,
            personality=bot.personality.value,
            system_prompt=bot.system_prompt,
            context=context_messages,
            temperature=bot.temperature,
            model=bot.model_name
        )
        used_rag = len(source_docs) > 0
    except Exception as e:
        # Fallback to simple response
        print(f"AI Generation Error: {e}")
        bot_response_text = f"Thank you for your message! I'm {bot.name}. How can I help you today?"
        source_docs = []
        used_rag = False

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # Save bot response
    bot_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=bot_response_text,
        model_used=bot.model_name,
        response_time_ms=response_time_ms,
        used_rag=used_rag,
        source_documents=str(source_docs) if source_docs else None
    )
    db.add(bot_message)

    # Update session timestamp
    session.last_message_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user_message)

    # Send webhook in background if configured
    if bot.send_lead_webhook and bot.n8n_webhook_url:
        background_tasks.add_task(
            send_conversation_to_n8n,
            bot.n8n_webhook_url,
            {
                "session_id": session.session_id,
                "message": message_data.message,
                "response": bot_response_text,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    return ChatResponse(
        session_id=session.session_id,
        message=user_message,
        bot_response=bot_response_text,
    )


@router.get("/sessions", response_model=list[ChatSessionSchema])
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    bot_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List chat sessions for user's bots (optimized with pagination)"""

    # Build optimized query with minimal joins
    query = (
        select(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
        .order_by(desc(ChatSession.last_message_at))
        .offset(skip)
        .limit(limit)
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
    """Get chat session with messages (optimized with eager loading)"""

    # Single query with eager loading
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
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

    return session


@router.patch("/sessions/{session_id}", response_model=ChatSessionSchema)
async def update_session(
    session_id: str,
    session_update: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update chat session (optimized)"""

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

    # Batch update
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)

    # Invalidate cache
    await cache_delete(f"session:{session_id}")

    return session
