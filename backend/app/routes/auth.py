"""Auth routes — signup, login, me."""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import SignupRequest, LoginRequest, TokenResponse, APIResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=APIResponse)
async def signup(req: SignupRequest):
    db = get_db()
    existing = await db.users.find_one({"email": req.email.lower().strip()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc).isoformat()
    result = await db.users.insert_one({
        "name": req.name.strip(),
        "email": req.email.lower().strip(),
        "passwordHash": hash_password(req.password),
        "createdAt": now,
        "updatedAt": now,
    })
    user_id = str(result.inserted_id)

    # Create empty profile
    await db.profiles.insert_one({
        "userId": user_id,
        "fullName": req.name.strip(),
        "email": req.email.lower().strip(),
        "phone": "", "location": "", "relocation": "",
        "workAuthorization": "", "availability": "", "rate": "",
        "linkedin": "", "github": "", "portfolio": "", "headline": "",
        "skills": [], "experience": [], "education": [],
        "projects": [], "certifications": [],
        "preferredLocations": [], "preferredWorkplaceTypes": [],
        "completeness": 0,
        "createdAt": now, "updatedAt": now,
    })

    # Create default settings
    await db.settings.insert_one({
        "userId": user_id,
        "theme": "system",
        "defaultApplicationMode": "AUTO_APPLY",
        "defaultAiThreshold": 70,
        "defaultMaxApplications": 50,
        "defaultCustomizeResume": False,
        "defaultResumeId": "",
        "sendingPacingMs": 4000,
        "dataRetentionDays": 90,
        "createdAt": now,
    })

    token = create_access_token(user_id, req.email)
    return APIResponse(data={
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": req.name, "email": req.email},
    })


@router.post("/login", response_model=APIResponse)
async def login(req: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"email": req.email.lower().strip()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(req.password, user.get("passwordHash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(user["_id"])
    token = create_access_token(user_id, user["email"])
    return APIResponse(data={
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": user.get("name", ""), "email": user["email"]},
    })


@router.get("/me", response_model=APIResponse)
async def me(user=Depends(get_current_user)):
    return APIResponse(data=user)



