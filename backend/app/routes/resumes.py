"""Resume routes — upload, list, delete, set default."""
import os, uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user
from app.config import RESUME_DIR, MAX_UPLOAD_SIZE
from app.models import APIResponse
from app.services.resume_service import extract_text

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXT = {".pdf", ".docx"}


def _serialize(r: dict) -> dict:
    r["id"] = str(r.pop("_id", ""))
    return r


@router.get("", response_model=APIResponse)
async def list_resumes(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.resumes.find({"userId": user["id"]}).sort("createdAt", -1)
    resumes = [_serialize(r) async for r in cursor]
    return APIResponse(data=resumes)


@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    db = get_db()

    # Validate
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX allowed")
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_UPLOAD_SIZE // 1024 // 1024}MB)")

    # Save file
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = RESUME_DIR / filename
    filepath.write_bytes(content)

    # Extract text
    extracted = extract_text(str(filepath))

    now = datetime.now(timezone.utc).isoformat()

    # Check if first resume → make default
    existing_count = await db.resumes.count_documents({"userId": user["id"]})
    is_default = existing_count == 0

    # If setting as default, unset others
    if is_default:
        await db.resumes.update_many(
            {"userId": user["id"]},
            {"$set": {"isDefault": False}},
        )

    result = await db.resumes.insert_one({
        "userId": user["id"],
        "filename": filename,
        "originalName": file.filename,
        "mimeType": file.content_type or "application/pdf",
        "sizeBytes": len(content),
        "storageKey": str(filepath),
        "status": "READY",
        "isDefault": is_default,
        "extractedText": extracted[:50000],
        "createdAt": now,
    })

    resume = await db.resumes.find_one({"_id": result.inserted_id})
    return APIResponse(data=_serialize(resume))


@router.delete("/{resume_id}", response_model=APIResponse)
async def delete_resume(resume_id: str, user=Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"_id": ObjectId(resume_id), "userId": user["id"]})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete file
    try:
        Path(resume["storageKey"]).unlink(missing_ok=True)
    except Exception:
        pass

    await db.resumes.delete_one({"_id": ObjectId(resume_id)})

    # If was default, set another as default
    if resume.get("isDefault"):
        next_resume = await db.resumes.find_one(
            {"userId": user["id"]},
            sort=[("createdAt", -1)],
        )
        if next_resume:
            await db.resumes.update_one(
                {"_id": next_resume["_id"]},
                {"$set": {"isDefault": True}},
            )

    return APIResponse(data={"deleted": True})


@router.post("/{resume_id}/default", response_model=APIResponse)
async def set_default_resume(resume_id: str, user=Depends(get_current_user)):
    db = get_db()
    resume = await db.resumes.find_one({"_id": ObjectId(resume_id), "userId": user["id"]})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    await db.resumes.update_many({"userId": user["id"]}, {"$set": {"isDefault": False}})
    await db.resumes.update_one({"_id": ObjectId(resume_id)}, {"$set": {"isDefault": True}})
    return APIResponse(data={"isDefault": True})


@router.get("/{resume_id}/download")
async def download_resume(resume_id: str, user=Depends(get_current_user)):
    from fastapi.responses import FileResponse
    db = get_db()
    resume = await db.resumes.find_one({"_id": ObjectId(resume_id), "userId": user["id"]})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    filepath = resume["storageKey"]
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(filepath, filename=resume["originalName"])
