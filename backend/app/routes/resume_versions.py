"""Resume versions routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse

router = APIRouter(prefix="/resume-versions", tags=["resume-versions"])


def _serialize(v: dict) -> dict:
    v["id"] = str(v.pop("_id", ""))
    return v


@router.get("", response_model=APIResponse)
async def list_versions(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.resumeversions.find({"userId": user["id"]}).sort("createdAt", -1)
    versions = [_serialize(v) async for v in cursor]
    return APIResponse(data=versions)


@router.get("/{version_id}", response_model=APIResponse)
async def get_version(version_id: str, user=Depends(get_current_user)):
    db = get_db()
    version = await db.resumeversions.find_one({"_id": ObjectId(version_id), "userId": user["id"]})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return APIResponse(data=_serialize(version))


@router.delete("/{version_id}", response_model=APIResponse)
async def delete_version(version_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.resumeversions.delete_one({"_id": ObjectId(version_id), "userId": user["id"]})
    return APIResponse(data={"deleted": True})
