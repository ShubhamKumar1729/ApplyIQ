"""Profile routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import ProfileUpdate, APIResponse
from app.services.resume_service import calculate_profile_completeness

router = APIRouter(prefix="/profile", tags=["profile"])


def _serialize(p: dict) -> dict:
    p["id"] = str(p.pop("_id", ""))
    return p


@router.get("", response_model=APIResponse)
async def get_profile(user=Depends(get_current_user)):
    db = get_db()
    profile = await db.profiles.find_one({"userId": user["id"]})
    if not profile:
        return APIResponse(data={})
    return APIResponse(data=_serialize(profile))


@router.put("", response_model=APIResponse)
async def update_profile(req: ProfileUpdate, user=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

    # Calculate completeness
    existing = await db.profiles.find_one({"userId": user["id"]})
    merged = {**(existing or {}), **update_data}
    update_data["completeness"] = calculate_profile_completeness(merged)

    await db.profiles.update_one(
        {"userId": user["id"]},
        {"$set": update_data},
        upsert=True,
    )
    profile = await db.profiles.find_one({"userId": user["id"]})
    return APIResponse(data=_serialize(profile))
