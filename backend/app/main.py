"""ApplyIQ — FastAPI Backend"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root for existing code imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import connect_db, disconnect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


app = FastAPI(
    title="ApplyIQ",
    description="AI-powered job application automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from app.routes.auth import router as auth_router
from app.routes.profile import router as profile_router
from app.routes.resumes import router as resumes_router
from app.routes.resume_versions import router as versions_router
from app.routes.searches import router as searches_router
from app.routes.applications import router as applications_router
from app.routes.jobs import router as jobs_router
from app.routes.dashboard import router as dashboard_router
from app.routes.analytics import router as analytics_router
from app.routes.automation import router as automation_router
from app.routes.notifications import router as notifications_router
from app.routes.settings import router as settings_router
from app.routes.ai import router as ai_router

app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(versions_router, prefix="/api")
app.include_router(searches_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(automation_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(ai_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"ok": True, "message": "ApplyIQ is running"}
