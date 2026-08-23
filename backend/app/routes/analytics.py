"""Analytics routes."""
from fastapi import APIRouter, Depends
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=APIResponse)
async def analytics(user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]

    # Applications over time (last 30 days)
    apps_over_time = []
    from datetime import datetime, timedelta, timezone
    for i in range(29, -1, -1):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        next_day = (datetime.now(timezone.utc) - timedelta(days=i - 1)).strftime("%Y-%m-%d")
        count = await db.applications.count_documents({
            "userId": uid,
            "createdAt": {"$gte": day, "$lt": next_day},
        })
        apps_over_time.append({"date": day, "count": count})

    # Status funnel
    statuses = ["AI_MATCHED", "PREPARED", "EMAIL_SENT", "APPLIED", "RESPONSE",
                "INTERVIEW", "OFFER", "REJECTED", "FAILED", "SKIPPED"]
    funnel = {}
    for s in statuses:
        funnel[s] = await db.applications.count_documents({"userId": uid, "status": s})

    # Per-search performance
    search_perf = []
    cursor = db.jobsearches.find({"userId": uid})
    async for search in cursor:
        sid = str(search["_id"])
        apps_count = await db.applications.count_documents({"userId": uid, "searchId": sid})
        sent_count = await db.applications.count_documents({"userId": uid, "searchId": sid, "status": "EMAIL_SENT"})
        search_perf.append({
            "searchId": sid,
            "name": search.get("name", ""),
            "applications": apps_count,
            "sent": sent_count,
        })

    # Per-role performance
    role_perf = []
    roles_seen = {}
    cursor = db.applications.find({"userId": uid, "roleKey": {"$ne": ""}})
    async for app in cursor:
        rk = app.get("roleKey", "Unknown")
        if rk not in roles_seen:
            roles_seen[rk] = {"roleKey": rk, "applications": 0, "sent": 0}
        roles_seen[rk]["applications"] += 1
        if app.get("status") == "EMAIL_SENT":
            roles_seen[rk]["sent"] += 1
    role_perf = list(roles_seen.values())

    # Totals
    total_apps = await db.applications.count_documents({"userId": uid})
    total_sent = await db.applications.count_documents({"userId": uid, "status": "EMAIL_SENT"})
    total_responses = await db.applications.count_documents({"userId": uid, "status": {"$in": ["RESPONSE", "INTERVIEW", "OFFER"]}})
    total_interviews = await db.applications.count_documents({"userId": uid, "status": "INTERVIEW"})
    total_offers = await db.applications.count_documents({"userId": uid, "status": "OFFER"})
    total_rejected = await db.applications.count_documents({"userId": uid, "status": "REJECTED"})

    return APIResponse(data={
        "applicationsOverTime": apps_over_time,
        "statusFunnel": funnel,
        "perSearchPerformance": search_perf,
        "perRolePerformance": role_perf,
        "totalApplications": total_apps,
        "totalSent": total_sent,
        "totalResponses": total_responses,
        "totalInterviews": total_interviews,
        "totalOffers": total_offers,
        "totalRejected": total_rejected,
    })
