"""Dashboard routes."""
from fastapi import APIRouter, Depends
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse
from app.services.resume_service import calculate_profile_completeness

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=APIResponse)
async def dashboard_stats(user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]

    # Counts
    total_apps = await db.applications.count_documents({"userId": uid})
    sent_apps = await db.applications.count_documents({"userId": uid, "status": "EMAIL_SENT"})
    relevant = await db.aievaluations.count_documents({"userId": uid, "relevant": True})
    active_searches = await db.jobsearches.count_documents({"userId": uid, "archived": False, "paused": False})
    responses = await db.applications.count_documents({"userId": uid, "status": {"$in": ["RESPONSE", "INTERVIEW", "OFFER"]}})

    response_rate = (responses / sent_apps * 100) if sent_apps > 0 else 0.0

    # Profile completeness
    profile = await db.profiles.find_one({"userId": uid})
    completeness = calculate_profile_completeness(profile or {})

    # Recent runs
    recent_runs = []
    cursor = db.automationruns.find({"userId": uid}).sort("createdAt", -1).limit(5)
    async for run in cursor:
        run["id"] = str(run.pop("_id", ""))
        recent_runs.append(run)

    # Recent applications
    recent_apps = []
    cursor = db.applications.find({"userId": uid}).sort("createdAt", -1).limit(10)
    async for app in cursor:
        app["id"] = str(app.pop("_id", ""))
        recent_apps.append(app)

    # Live automation
    live = await db.automationruns.find_one({
        "userId": uid,
        "status": {"$in": ["RUNNING", "PAUSED"]},
    })
    if live:
        live["id"] = str(live.pop("_id", ""))

    return APIResponse(data={
        "totalApplications": total_apps,
        "applicationsSent": sent_apps,
        "relevantJobs": relevant,
        "responseRate": round(response_rate, 1),
        "activeSearches": active_searches,
        "profileCompleteness": completeness,
        "recentRuns": recent_runs,
        "recentApplications": recent_apps,
        "liveAutomation": live,
    })
