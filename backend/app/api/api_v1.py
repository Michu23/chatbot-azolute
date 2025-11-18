from fastapi import APIRouter
from app.api.endpoints import auth, users, organizations, bots, chat, leads, knowledge, dashboard

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(bots.router, prefix="/bots", tags=["Bots"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
