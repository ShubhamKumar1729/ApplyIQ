"""AI routes — evaluation, resume customization, message generation."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.auth import get_current_user
from app.models import APIResponse
from app.services.ai_service import evaluate_relevance, customize_resume, generate_application_message

router = APIRouter(prefix="/ai", tags=["ai"])


class EvaluateRequest(BaseModel):
    jobId: str
    jobTitle: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    roleTitle: str = ""
    roleQuery: str = ""


class CustomizeRequest(BaseModel):
    jobId: str
    jobTitle: str = ""
    jobDescription: str = ""
    resumeText: str = ""


class MessageRequest(BaseModel):
    jobTitle: str = ""
    company: str = ""
    recruiterName: str = ""
    description: str = ""
    matchingSkills: List[str] = []


@router.post("/evaluate", response_model=APIResponse)
async def ai_evaluate(req: EvaluateRequest, user=Depends(get_current_user)):
    db = get_db()
    profile = await db.profiles.find_one({"userId": user["id"]}) or {}

    resume = await db.resumes.find_one({"userId": user["id"], "isDefault": True})
    resume_text = resume.get("extractedText", "") if resume else ""

    role = {"title": req.roleTitle, "query": req.roleQuery}
    result = evaluate_relevance(
        candidate=profile,
        role=role,
        job_title=req.jobTitle,
        company=req.company,
        location=req.location,
        description=req.description,
        resume_text=resume_text,
    )

    # Store evaluation
    from datetime import datetime, timezone
    await db.aievaluations.insert_one({
        "userId": user["id"],
        "jobId": req.jobId,
        "relevant": result["relevant"],
        "score": result["score"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "matchingSkills": result["matchingSkills"],
        "missingRequirements": result["missingRequirements"],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })

    return APIResponse(data=result)


@router.post("/customize-resume", response_model=APIResponse)
async def ai_customize_resume(req: CustomizeRequest, user=Depends(get_current_user)):
    db = get_db()
    profile = await db.profiles.find_one({"userId": user["id"]}) or {}

    result = customize_resume(
        resume_text=req.resumeText,
        job_description=req.jobDescription,
        job_title=req.jobTitle,
        candidate=profile,
    )

    return APIResponse(data=result)


@router.post("/generate-message", response_model=APIResponse)
async def ai_generate_message(req: MessageRequest, user=Depends(get_current_user)):
    db = get_db()
    profile = await db.profiles.find_one({"userId": user["id"]}) or {}

    message = generate_application_message(
        candidate=profile,
        job_title=req.jobTitle,
        company=req.company,
        recruiter_name=req.recruiterName,
        description=req.description,
        matching_skills=req.matchingSkills,
    )

    return APIResponse(data={"message": message})
