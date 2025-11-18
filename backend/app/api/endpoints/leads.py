from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
import csv
import io

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.lead import Lead
from app.models.chat import ChatSession
from app.models.bot import Bot
from app.models.organization import Organization
from app.schemas.lead import Lead as LeadSchema, LeadCreate, LeadUpdate, LeadList

router = APIRouter()


@router.post("/", response_model=LeadSchema)
async def create_lead(
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a lead from chat session (public endpoint)"""
    # Get session
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == lead_data.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create lead
    lead = Lead(
        session_id=session.id,
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        message=lead_data.message,
        source_url=session.source_url,
    )
    db.add(lead)

    # Update session
    session.is_lead = True
    if lead.email:
        session.visitor_email = lead.email
    if lead.name:
        session.visitor_name = lead.name
    if lead.phone:
        session.visitor_phone = lead.phone

    await db.commit()
    await db.refresh(lead)

    # TODO: Send webhook to n8n if configured

    return lead


@router.get("/", response_model=LeadList)
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all leads for user's organizations"""
    result = await db.execute(
        select(Lead)
        .join(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
        .order_by(desc(Lead.created_at))
        .offset(skip)
        .limit(limit)
    )
    leads = result.scalars().all()

    # Count total
    count_result = await db.execute(
        select(Lead)
        .join(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    return LeadList(leads=leads, total=total)


@router.get("/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get lead by ID"""
    result = await db.execute(
        select(Lead)
        .join(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(
            Lead.id == lead_id,
            Organization.owner_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update lead"""
    result = await db.execute(
        select(Lead)
        .join(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(
            Lead.id == lead_id,
            Organization.owner_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields
    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/export/csv")
async def export_leads_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export leads to CSV"""
    result = await db.execute(
        select(Lead)
        .join(ChatSession)
        .join(Bot)
        .join(Organization)
        .where(Organization.owner_id == current_user.id)
        .order_by(desc(Lead.created_at))
    )
    leads = result.scalars().all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Name', 'Email', 'Phone', 'Company', 'Message',
        'Source URL', 'Created At', 'Is Qualified', 'Is Contacted'
    ])

    for lead in leads:
        writer.writerow([
            lead.id,
            lead.name or '',
            lead.email or '',
            lead.phone or '',
            lead.company or '',
            lead.message or '',
            lead.source_url or '',
            lead.created_at.isoformat(),
            lead.is_qualified,
            lead.is_contacted,
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=leads_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
