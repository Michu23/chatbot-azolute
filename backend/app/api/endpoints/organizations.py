from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify
import secrets

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.organization import Organization
from app.models.bot import Bot
from app.schemas.organization import Organization as OrgSchema, OrganizationCreate, OrganizationUpdate
from app.schemas.onboarding import OnboardingComplete, OnboardingResponse

router = APIRouter()


@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    onboarding_data: OnboardingComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete onboarding wizard and create organization + bot"""
    # Create organization
    slug = slugify(onboarding_data.step2.business_name)
    # Ensure unique slug
    counter = 1
    while True:
        result = await db.execute(select(Organization).where(Organization.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{slugify(onboarding_data.step2.business_name)}-{counter}"
        counter += 1

    organization = Organization(
        name=onboarding_data.step2.business_name,
        slug=slug,
        owner_id=current_user.id,
        website_domain=onboarding_data.step2.website_domain,
        primary_color=onboarding_data.step2.primary_color,
    )
    db.add(organization)
    await db.flush()

    # Create bot
    bot_id = secrets.token_urlsafe(16)
    bot = Bot(
        organization_id=organization.id,
        name=onboarding_data.step2.bot_name,
        bot_id=bot_id,
        personality=onboarding_data.step1.personality,
        custom_persona=onboarding_data.step1.custom_persona,
        welcome_message=onboarding_data.step2.welcome_message,
        primary_color=onboarding_data.step2.primary_color,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)

    # Generate widget code
    widget_script = f'<script src="{settings.FRONTEND_URL}/widget.js" data-bot-id="{bot_id}"></script>'
    widget_iframe = f'<iframe src="{settings.FRONTEND_URL}/widget?bot={bot_id}" style="position:fixed;bottom:20px;right:20px;width:400px;height:600px;border:none;"></iframe>'

    return OnboardingResponse(
        organization_id=organization.id,
        bot_id=bot_id,
        widget_script=widget_script,
        widget_iframe=widget_iframe,
    )


@router.get("/", response_model=list[OrgSchema])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's organizations"""
    result = await db.execute(
        select(Organization).where(Organization.owner_id == current_user.id)
    )
    organizations = result.scalars().all()
    return organizations


@router.get("/{org_id}", response_model=OrgSchema)
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get organization by ID"""
    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.owner_id == current_user.id
        )
    )
    organization = result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.patch("/{org_id}", response_model=OrgSchema)
async def update_organization(
    org_id: int,
    org_update: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update organization"""
    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.owner_id == current_user.id
        )
    )
    organization = result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Update fields
    if org_update.name:
        organization.name = org_update.name
    if org_update.website_domain:
        organization.website_domain = org_update.website_domain
    if org_update.primary_color:
        organization.primary_color = org_update.primary_color
    if org_update.logo_url:
        organization.logo_url = org_update.logo_url

    await db.commit()
    await db.refresh(organization)
    return organization
