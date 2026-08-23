"""Notification routes."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _serialize(n: dict) -> dict:
    n["id"] = str(n.pop("_id", ""))
    return n


@router.get("", response_model=APIResponse)
async def list_notifications(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.notifications.find({"userId": user["id"]}).sort("createdAt", -1).limit(50)
    notifs = [_serialize(n) async for n in cursor]
    unread = await db.notifications.count_documents({"userId": user["id"], "read": False})
    return APIResponse(data={"notifications": notifs, "unreadCount": unread})


@router.post("/{notif_id}/read", response_model=APIResponse)
async def mark_read(notif_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.notifications.update_one(
        {"_id": ObjectId(notif_id), "userId": user["id"]},
        {"$set": {"read": True}},
    )
    return APIResponse(data={"read": True})


@router.post("/read-all", response_model=APIResponse)
async def mark_all_read(user=Depends(get_current_user)):
    db = get_db()
    await db.notifications.update_many(
        {"userId": user["id"], "read": False},
        {"$set": {"read": True}},
    )
    return APIResponse(data={"allRead": True})


@router.delete("/{notif_id}", response_model=APIResponse)
async def delete_notification(notif_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.notifications.delete_one({"_id": ObjectId(notif_id), "userId": user["id"]})
    return APIResponse(data={"deleted": True})
