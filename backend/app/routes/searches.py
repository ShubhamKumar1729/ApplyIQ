"""Job search routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import JobSearchCreate, JobSearchUpdate, APIResponse

router = APIRouter(prefix="/job-searches", tags=["job-searches"])


def _serialize(s: dict) -> dict:
    s["id"] = str(s.pop("_id", ""))
    return s


@router.get("", response_model=APIResponse)
async def list_searches(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.jobsearches.find({"userId": user["id"]}).sort("createdAt", -1)
    searches = [_serialize(s) async for s in cursor]
    return APIResponse(data=searches)


@router.post("", response_model=APIResponse)
async def create_search(req: JobSearchCreate, user=Depends(get_current_user)):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Generate role keys
    roles = []
    for i, role in enumerate(req.roles):
        r = role.dict()
        if not r.get("key"):
            r["key"] = f"role_{i+1}"
        roles.append(r)

    data = {
        "userId": user["id"],
        "name": req.name.strip(),
        "description": req.description or "",
        "roles": roles,
        "applicationMode": req.applicationMode.value if hasattr(req.applicationMode, 'value') else req.applicationMode,
        "customizeResume": req.customizeResume,
        "aiThreshold": req.aiThreshold,
        "globalMaxApplications": req.globalMaxApplications,
        "ccEmails": req.ccEmails,
        "bccEmails": req.bccEmails,
        "schedule": req.schedule,
        "paused": False,
        "archived": False,
        "createdAt": now,
        "updatedAt": now,
    }

    result = await db.jobsearches.insert_one(data)
    search = await db.jobsearches.find_one({"_id": result.inserted_id})
    return APIResponse(data=_serialize(search))


@router.get("/{search_id}", response_model=APIResponse)
async def get_search(search_id: str, user=Depends(get_current_user)):
    db = get_db()
    search = await db.jobsearches.find_one({"_id": ObjectId(search_id), "userId": user["id"]})
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return APIResponse(data=_serialize(search))


@router.put("/{search_id}", response_model=APIResponse)
async def update_search(search_id: str, req: JobSearchUpdate, user=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if "roles" in update_data and update_data["roles"]:
        for i, role in enumerate(update_data["roles"]):
            if not role.get("key"):
                role["key"] = f"role_{i+1}"
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

    await db.jobsearches.update_one(
        {"_id": ObjectId(search_id), "userId": user["id"]},
        {"$set": update_data},
    )
    search = await db.jobsearches.find_one({"_id": ObjectId(search_id)})
    return APIResponse(data=_serialize(search))


@router.delete("/{search_id}", response_model=APIResponse)
async def delete_search(search_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.jobsearches.delete_one({"_id": ObjectId(search_id), "userId": user["id"]})
    return APIResponse(data={"deleted": True})


@router.post("/{search_id}/duplicate", response_model=APIResponse)
async def duplicate_search(search_id: str, user=Depends(get_current_user)):
    db = get_db()
    search = await db.jobsearches.find_one({"_id": ObjectId(search_id), "userId": user["id"]})
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    now = datetime.now(timezone.utc).isoformat()
    new_search = {k: v for k, v in search.items() if k not in ("_id", "createdAt", "updatedAt")}
    new_search["name"] = f"{search['name']} (Copy)"
    new_search["paused"] = True
    new_search["createdAt"] = now
    new_search["updatedAt"] = now

    result = await db.jobsearches.insert_one(new_search)
    created = await db.jobsearches.find_one({"_id": result.inserted_id})
    return APIResponse(data=_serialize(created))
