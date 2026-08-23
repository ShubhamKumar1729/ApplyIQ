"""Settings routes."""
from fastapi import APIRouter, Depends
from app.database import get_db
from app.auth import get_current_user
from app.models import SettingsUpdate, APIResponse

router = APIRouter(prefix="/settings", tags=["settings"])


def _serialize(s: dict) -> dict:
    s["id"] = str(s.pop("_id", ""))
    return s


@router.get("", response_model=APIResponse)
async def get_settings(user=Depends(get_current_user)):
    db = get_db()
    settings = await db.settings.find_one({"userId": user["id"]})
    if not settings:
        return APIResponse(data={
            "theme": "system", "defaultApplicationMode": "AUTO_APPLY",
            "defaultAiThreshold": 70, "defaultMaxApplications": 50,
            "defaultCustomizeResume": False, "defaultResumeId": "",
            "sendingPacingMs": 4000, "dataRetentionDays": 90,
        })
    return APIResponse(data=_serialize(settings))


@router.put("", response_model=APIResponse)
async def update_settings(req: SettingsUpdate, user=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    await db.settings.update_one(
        {"userId": user["id"]},
        {"$set": update_data},
        upsert=True,
    )
    settings = await db.settings.find_one({"userId": user["id"]})
    return APIResponse(data=_serialize(settings) if settings else {})
