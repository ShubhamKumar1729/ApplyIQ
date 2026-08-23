"""Application routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import ApplicationApprove, APIResponse

router = APIRouter(prefix="/applications", tags=["applications"])


def _serialize(a: dict) -> dict:
    a["id"] = str(a.pop("_id", ""))
    return a


@router.get("", response_model=APIResponse)
async def list_applications(
    status: str = None,
    search_id: str = None,
    role_key: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(get_current_user),
):
    db = get_db()
    query = {"userId": user["id"]}
    if status:
        query["status"] = status
    if search_id:
        query["searchId"] = search_id
    if role_key:
        query["roleKey"] = role_key

    total = await db.applications.count_documents(query)
    cursor = db.applications.find(query).sort("createdAt", -1).skip((page - 1) * limit).limit(limit)
    apps = [_serialize(a) async for a in cursor]
    return APIResponse(data={"applications": apps, "total": total, "page": page, "limit": limit})


@router.get("/{app_id}", response_model=APIResponse)
async def get_application(app_id: str, user=Depends(get_current_user)):
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id), "userId": user["id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Attach job data if available
    if app.get("jobId"):
        job = await db.jobs.find_one({"_id": ObjectId(app["jobId"])})
        if job:
            job["id"] = str(job.pop("_id", ""))
            app["job"] = job

    return APIResponse(data=_serialize(app))


@router.patch("/{app_id}/status", response_model=APIResponse)
async def update_status(app_id: str, status: str, user=Depends(get_current_user)):
    db = get_db()
    valid = {"AI_MATCHED", "PREPARED", "EMAIL_SENT", "APPLIED", "RESPONSE",
             "INTERVIEW", "OFFER", "REJECTED", "FAILED", "SKIPPED"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")

    await db.applications.update_one(
        {"_id": ObjectId(app_id), "userId": user["id"]},
        {"$set": {"status": status, "updatedAt": datetime.now(timezone.utc).isoformat()}},
    )
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    return APIResponse(data=_serialize(app))


@router.post("/{app_id}/approve", response_model=APIResponse)
async def approve_application(app_id: str, req: ApplicationApprove, user=Depends(get_current_user)):
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id), "userId": user["id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if req.approved:
        # Send the email
        from app.services.email_adapter import send_application_email
        result = send_application_email(
            to_email=app.get("recruiterEmail", ""),
            subject=app.get("emailSubject", ""),
            body=app.get("emailBody", ""),
            resume_path=app.get("resumePath", ""),
            cc_emails=app.get("ccEmails", []),
            bcc_emails=app.get("bccEmails", []),
            post_link=app.get("postLink", ""),
            role_name=app.get("roleKey", ""),
            user_email=user.get("email", ""),
        )
        new_status = "EMAIL_SENT" if result["success"] else "FAILED"
        error_msg = "" if result["success"] else result.get("error", "")
    else:
        new_status = "SKIPPED"
        error_msg = ""

    await db.applications.update_one(
        {"_id": ObjectId(app_id)},
        {"$set": {
            "status": new_status,
            "pendingApproval": False,
            "error": error_msg,
            "sentAt": datetime.now(timezone.utc).isoformat() if new_status == "EMAIL_SENT" else None,
            "notes": req.notes or "",
        }},
    )
    updated = await db.applications.find_one({"_id": ObjectId(app_id)})
    return APIResponse(data=_serialize(updated))


@router.post("/{app_id}/feedback", response_model=APIResponse)
async def add_feedback(app_id: str, helpful: bool, comment: str = "", user=Depends(get_current_user)):
    db = get_db()
    await db.applications.update_one(
        {"_id": ObjectId(app_id), "userId": user["id"]},
        {"$set": {"feedback": {"helpful": helpful, "comment": comment}}},
    )
    return APIResponse(data={"updated": True})


@router.delete("/{app_id}", response_model=APIResponse)
async def delete_application(app_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.applications.delete_one({"_id": ObjectId(app_id), "userId": user["id"]})
    return APIResponse(data={"deleted": True})
