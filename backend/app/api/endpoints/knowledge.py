from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from app.models.knowledge import KnowledgeSource, SourceType, IndexStatus
from app.schemas.knowledge import (
    KnowledgeSource as KnowledgeSourceSchema,
    KnowledgeSourceCreate,
    KnowledgeSourceUpdate,
    KnowledgeSourceList,
)

router = APIRouter()


@router.post("/", response_model=KnowledgeSourceSchema)
async def create_knowledge_source(
    source_data: KnowledgeSourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a knowledge source"""
    # Verify bot belongs to user
    result = await db.execute(
        select(Bot)
        .join(Organization)
        .where(
            Bot.id == source_data.bot_id,
            Organization.owner_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Create knowledge source
    source = KnowledgeSource(
        bot_id=source_data.bot_id,
        source_type=source_data.source_type,
        name=source_data.name,
        url=source_data.url,
        content=source_data.content,
        status=IndexStatus.PENDING,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    # TODO: Trigger background task to index the source

    return source


@router.post("/upload-pdf", response_model=KnowledgeSourceSchema)
async def upload_pdf(
    bot_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload PDF file as knowledge source"""
    # Verify bot belongs to user
    result = await db.execute(
        select(Bot)
        .join(Organization)
        .where(
            Bot.id == bot_id,
            Organization.owner_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{bot_id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create knowledge source
    source = KnowledgeSource(
        bot_id=bot_id,
        source_type=SourceType.PDF,
        name=file.filename,
        file_path=file_path,
        status=IndexStatus.PENDING,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    # TODO: Trigger background task to process PDF and create embeddings

    return source


@router.get("/bot/{bot_id}", response_model=KnowledgeSourceList)
async def list_knowledge_sources(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List knowledge sources for a bot"""
    # Verify bot belongs to user
    result = await db.execute(
        select(Bot)
        .join(Organization)
        .where(
            Bot.id == bot_id,
            Organization.owner_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Get sources
    result = await db.execute(
        select(KnowledgeSource).where(KnowledgeSource.bot_id == bot_id)
    )
    sources = result.scalars().all()

    return KnowledgeSourceList(sources=sources, total=len(sources))


@router.delete("/{source_id}")
async def delete_knowledge_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a knowledge source"""
    result = await db.execute(
        select(KnowledgeSource)
        .join(Bot)
        .join(Organization)
        .where(
            KnowledgeSource.id == source_id,
            Organization.owner_id == current_user.id
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Delete file if exists
    if source.file_path and os.path.exists(source.file_path):
        os.remove(source.file_path)

    await db.delete(source)
    await db.commit()

    return {"message": "Knowledge source deleted successfully"}


@router.post("/{source_id}/reindex")
async def reindex_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger re-indexing of a knowledge source"""
    result = await db.execute(
        select(KnowledgeSource)
        .join(Bot)
        .join(Organization)
        .where(
            KnowledgeSource.id == source_id,
            Organization.owner_id == current_user.id
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.status = IndexStatus.PENDING
    await db.commit()

    # TODO: Trigger background task to re-index

    return {"message": "Re-indexing started"}
