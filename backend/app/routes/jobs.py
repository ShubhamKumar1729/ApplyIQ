"""Jobs routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _serialize(j: dict) -> dict:
    j["id"] = str(j.pop("_id", ""))
    return j


@router.get("", response_model=APIResponse)
async def list_jobs(
    search_id: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(get_current_user),
):
    db = get_db()
    query = {"userId": user["id"]}
    if search_id:
        query["searchId"] = search_id

    total = await db.jobs.count_documents(query)
    cursor = db.jobs.find(query).sort("createdAt", -1).skip((page - 1) * limit).limit(limit)
    jobs = [_serialize(j) async for j in cursor]
    return APIResponse(data={"jobs": jobs, "total": total, "page": page, "limit": limit})


@router.get("/{job_id}", response_model=APIResponse)
async def get_job(job_id: str, user=Depends(get_current_user)):
    db = get_db()
    job = await db.jobs.find_one({"_id": ObjectId(job_id), "userId": user["id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Attach AI evaluation if available
    eval_doc = await db.aievaluations.find_one({"jobId": job_id, "userId": user["id"]})
    if eval_doc:
        eval_doc["id"] = str(eval_doc.pop("_id", ""))
        job["evaluation"] = eval_doc

    # Attach application if exists
    app = await db.applications.find_one({"jobId": job_id, "userId": user["id"]})
    if app:
        app["id"] = str(app.pop("_id", ""))
        job["application"] = app

    return APIResponse(data=_serialize(job))


@router.post("/{job_id}/save", response_model=APIResponse)
async def save_job(job_id: str, user=Depends(get_current_user)):
    db = get_db()
    job = await db.jobs.find_one({"_id": ObjectId(job_id), "userId": user["id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = await db.savedjobs.find_one({"userId": user["id"], "jobId": job_id})
    if existing:
        await db.savedjobs.delete_one({"_id": existing["_id"]})
        return APIResponse(data={"saved": False})

    await db.savedjobs.insert_one({
        "userId": user["id"],
        "jobId": job_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })
    return APIResponse(data={"saved": True})


@router.get("/saved/list", response_model=APIResponse)
async def list_saved_jobs(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.savedjobs.find({"userId": user["id"]}).sort("createdAt", -1)
    saved = []
    async for s in cursor:
        job = await db.jobs.find_one({"_id": ObjectId(s["jobId"])})
        if job:
            job["id"] = str(job.pop("_id", ""))
            job["savedAt"] = s.get("createdAt", "")
            saved.append(job)
    return APIResponse(data=saved)
