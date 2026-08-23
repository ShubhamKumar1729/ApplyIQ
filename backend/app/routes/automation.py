"""Automation routes — start, stop, pause, resume, status, logs."""
import asyncio, time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from bson import ObjectId
from app.database import get_db
from app.auth import get_current_user, decode_token
from app.models import AutomationStartRequest, APIResponse

router = APIRouter(prefix="/automation", tags=["automation"])

# In-memory store for active automation tasks
_active_runs: dict = {}  # run_id -> asyncio.Task
_ws_connections: dict = {}  # user_id -> set of websockets


async def _notify_ws(user_id: str, event: dict):
    """Send event to all WebSocket connections for a user."""
    conns = _ws_connections.get(user_id, set())
    dead = set()
    for ws in conns:
        try:
            await ws.send_json(event)
        except Exception:
            dead.add(ws)
    conns -= dead


# ── WebSocket for real-time updates ─────────────────────────
@router.websocket("/ws")
async def automation_ws(websocket: WebSocket, token: str = ""):
    await websocket.accept()
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload["sub"]
    if user_id not in _ws_connections:
        _ws_connections[user_id] = set()
    _ws_connections[user_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Client can send ping, we respond with status
            if data == "ping":
                db = get_db()
                run = await db.automationruns.find_one({
                    "userId": user_id,
                    "status": {"$in": ["RUNNING", "PAUSED"]},
                })
                if run:
                    run["id"] = str(run.pop("_id", ""))
                    await websocket.send_json({"type": "status", "run": run})
                else:
                    await websocket.send_json({"type": "status", "run": None})
    except WebSocketDisconnect:
        _ws_connections.get(user_id, set()).discard(websocket)


# ── Start automation ────────────────────────────────────────
@router.post("/start", response_model=APIResponse)
async def start_automation(req: AutomationStartRequest, user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]

    # Check no other run is active
    existing = await db.automationruns.find_one({
        "userId": uid, "status": {"$in": ["RUNNING", "PAUSED"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Automation already running")

    # Load search config
    search = await db.jobsearches.find_one({
        "_id": ObjectId(req.searchId), "userId": uid
    })
    if not search:
        raise HTTPException(status_code=404, detail="Job search not found")

    # Create run
    now = datetime.now(timezone.utc).isoformat()
    run_data = {
        "userId": uid,
        "searchId": req.searchId,
        "status": "RUNNING",
        "jobsFound": 0,
        "jobsEvaluated": 0,
        "relevantCount": 0,
        "applicationsSent": 0,
        "skippedCount": 0,
        "failedCount": 0,
        "currentRoleKey": "",
        "currentJobId": "",
        "currentJobTitle": "",
        "globalMax": search.get("globalMaxApplications", 50),
        "startedAt": now,
        "finishedAt": None,
        "stoppedReason": "",
        "error": "",
        "createdAt": now,
    }
    result = await db.automationruns.insert_one(run_data)
    run_id = str(result.inserted_id)

    # Log start
    await db.automationlogs.insert_one({
        "userId": uid, "runId": run_id, "jobId": "",
        "level": "info", "message": f"[AUTOMATION] Started for search: {search['name']}",
        "createdAt": now,
    })

    await _notify_ws(uid, {
        "type": "automation_started",
        "runId": run_id,
        "message": "Automation started",
    })

    # Start background task
    task = asyncio.create_task(_run_automation(uid, run_id, search))

    def _on_done(t: asyncio.Task):
        _active_runs.pop(run_id, None)
        try:
            exc = t.exception()
        except asyncio.CancelledError:
            return
        if exc:
            print(f"Automation run {run_id} failed: {exc}")

    task.add_done_callback(_on_done)
    _active_runs[run_id] = task

    return APIResponse(data={"runId": run_id, "status": "RUNNING"})


# ── Stop automation ─────────────────────────────────────────
@router.post("/stop/{run_id}", response_model=APIResponse)
async def stop_automation(run_id: str, user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]
    run = await db.automationruns.find_one({"_id": ObjectId(run_id), "userId": uid})
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    task = _active_runs.get(run_id)
    if task:
        task.cancel()
        _active_runs.pop(run_id, None)

    now = datetime.now(timezone.utc).isoformat()
    await db.automationruns.update_one(
        {"_id": ObjectId(run_id)},
        {"$set": {"status": "STOPPED", "finishedAt": now, "stoppedReason": "User stopped"}},
    )
    await _notify_ws(uid, {"type": "automation_stopped", "runId": run_id})
    return APIResponse(data={"status": "STOPPED"})


# ── Pause/Resume ────────────────────────────────────────────
@router.post("/pause/{run_id}", response_model=APIResponse)
async def pause_automation(run_id: str, user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]
    await db.automationruns.update_one(
        {"_id": ObjectId(run_id), "userId": uid},
        {"$set": {"status": "PAUSED"}},
    )
    await _notify_ws(uid, {"type": "automation_paused", "runId": run_id})
    return APIResponse(data={"status": "PAUSED"})


@router.post("/resume/{run_id}", response_model=APIResponse)
async def resume_automation(run_id: str, user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]
    await db.automationruns.update_one(
        {"_id": ObjectId(run_id), "userId": uid},
        {"$set": {"status": "RUNNING"}},
    )
    await _notify_ws(uid, {"type": "automation_resumed", "runId": run_id})
    return APIResponse(data={"status": "RUNNING"})


# ── Status ──────────────────────────────────────────────────
@router.get("/status", response_model=APIResponse)
async def automation_status(user=Depends(get_current_user)):
    db = get_db()
    run = await db.automationruns.find_one({
        "userId": user["id"],
        "status": {"$in": ["RUNNING", "PAUSED"]},
    })
    if run:
        run["id"] = str(run.pop("_id", ""))
    return APIResponse(data=run)


@router.get("/runs", response_model=APIResponse)
async def list_runs(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.automationruns.find({"userId": user["id"]}).sort("createdAt", -1).limit(20)
    runs = []
    async for r in cursor:
        r["id"] = str(r.pop("_id", ""))
        runs.append(r)
    return APIResponse(data=runs)


# ── Logs ────────────────────────────────────────────────────
@router.get("/logs/{run_id}", response_model=APIResponse)
async def get_logs(run_id: str, limit: int = 100, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.automationlogs.find(
        {"userId": user["id"], "runId": run_id}
    ).sort("createdAt", -1).limit(limit)
    logs = []
    async for log in cursor:
        log["id"] = str(log.pop("_id", ""))
        logs.append(log)
    logs.reverse()
    return APIResponse(data=logs)


# ── Background Automation Engine ────────────────────────────
async def _run_automation(user_id: str, run_id: str, search: dict):
    """
    Main automation loop. Processes roles sequentially.
    Uses existing Playwright browser automation for LinkedIn.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    async def log(level: str, message: str, job_id: str = ""):
        await db.automationlogs.insert_one({
            "userId": user_id, "runId": run_id, "jobId": job_id,
            "level": level, "message": message,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })
        await _notify_ws(user_id, {"type": "log", "level": level, "message": message, "runId": run_id})

    async def update_run(fields: dict):
        await db.automationruns.update_one({"_id": ObjectId(run_id)}, {"$set": fields})
        await _notify_ws(user_id, {"type": "run_update", "runId": run_id, **fields})

    try:
        await log("info", "[AUTOMATION] Beginning job search processing…")

        # Load profile
        profile = await db.profiles.find_one({"userId": user_id}) or {}
        profile["id"] = str(profile.pop("_id", ""))

        # Load default resume
        resume = await db.resumes.find_one({"userId": user_id, "isDefault": True})
        resume_path = resume["storageKey"] if resume else ""

        roles = search.get("roles", [])
        global_sent = 0
        global_max = search.get("globalMaxApplications", 50)
        mode = search.get("applicationMode", "AUTO_APPLY")
        ai_threshold = search.get("aiThreshold", 70)
        customize = search.get("customizeResume", False)

        for role in roles:
            role_key = role.get("key", role.get("title", ""))
            role_max = role.get("maxApplications", 15)
            role_sent = 0

            await update_run({"currentRoleKey": role_key})
            await log("info", f"[ROLE] Processing: {role.get('title', role_key)}")

            # Check if run is still active
            run = await db.automationruns.find_one({"_id": ObjectId(run_id)})
            if run.get("status") == "STOPPED":
                break
            while run.get("status") == "PAUSED":
                await asyncio.sleep(2)
                run = await db.automationruns.find_one({"_id": ObjectId(run_id)})

            # ── Search LinkedIn (sync Playwright in a thread — Windows-safe) ──
            try:
                from app.config import LINKEDIN_PROFILE_DIR, SCROLL_ROUNDS
                from app.services.linkedin_scrape import scrape_role_posts

                query = role.get("query", role.get("title", ""))
                profile_dir = search.get("_profileDir") or LINKEDIN_PROFILE_DIR
                await log("info", f"[BROWSER] Opening LinkedIn for {role.get('title', '')}…")
                scrape = await asyncio.to_thread(
                    scrape_role_posts, query, profile_dir, SCROLL_ROUNDS
                )
                if not scrape.get("ok"):
                    await log("error", f"[BROWSER] Automation error: {scrape.get('error', 'unknown')[:300]}")
                    await update_run({
                        "status": "ERROR",
                        "error": (scrape.get("error") or "Playwright failed")[:500],
                        "finishedAt": datetime.now(timezone.utc).isoformat(),
                    })
                    return

                posts = scrape.get("posts") or []
                await log("info", "[SEARCH] Search page loaded")
                await log("info", f"[SEARCH] Found {len(posts)} posts with recruiter emails")

                for post in posts:
                    if global_sent >= global_max:
                        await log("info", "[LIMIT] Global application limit reached")
                        await update_run({"status": "COMPLETED", "finishedAt": datetime.now(timezone.utc).isoformat()})
                        return

                    if role_sent >= role_max:
                        await log("info", f"[LIMIT] Role limit reached ({role_max})")
                        break

                    run = await db.automationruns.find_one({"_id": ObjectId(run_id)})
                    if run.get("status") == "STOPPED":
                        break
                    while run.get("status") == "PAUSED":
                        await asyncio.sleep(2)
                        run = await db.automationruns.find_one({"_id": ObjectId(run_id)})

                    try:
                        text = post.get("text") or ""
                        emails = post.get("emails") or []
                        if not post.get("allowed", True):
                            await log("warn", f"[SKIP] Junk/non-genuine post: {post.get('skipReason', '')}")
                            await db.automationruns.update_one(
                                {"_id": ObjectId(run_id)},
                                {"$inc": {"skippedCount": 1}},
                            )
                            continue

                        await update_run({"jobsFound": global_sent + role_sent + 1})

                        for email in emails[:5]:
                            if global_sent >= global_max or role_sent >= role_max:
                                break

                            existing_app = await db.applications.find_one({
                                "userId": user_id,
                                "recruiterEmail": email,
                                "status": {"$ne": "SKIPPED"},
                            })
                            if existing_app:
                                await log("info", f"[SKIP] Duplicate application skipped: {email}")
                                continue

                            job_data = {
                                "userId": user_id,
                                "searchId": search.get("_id") and str(search["_id"]),
                                "source": "linkedin",
                                "sourceId": f"linkedin-post-{hash(text[:200])}-{email}",
                                "title": role.get("title", ""),
                                "company": "",
                                "location": role.get("location", ""),
                                "description": text[:5000],
                                "url": "",
                                "recruiterEmail": email,
                                "recruiterName": "",
                                "raw": {"postText": text[:2000]},
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                            }

                            try:
                                job_result = await db.jobs.insert_one(job_data)
                                job_id = str(job_result.inserted_id)
                            except Exception:
                                existing_job = await db.jobs.find_one({
                                    "userId": user_id, "sourceId": job_data["sourceId"]
                                })
                                if existing_job:
                                    job_id = str(existing_job["_id"])
                                else:
                                    continue

                            await log("info", f"[JOB] Found: {role.get('title', '')} - {email}")
                            await log("info", f"[EMAIL] Recruiter email found: {email}")

                            await log("info", "[AI] Sending complete job data to Groq…")
                            from app.services.ai_service import evaluate_relevance
                            eval_result = evaluate_relevance(
                                candidate=profile,
                                role=role,
                                job_title=role.get("title", ""),
                                company="",
                                location=role.get("location", ""),
                                description=text,
                                resume_text=resume.get("extractedText", "") if resume else "",
                            )

                            await db.aievaluations.insert_one({
                                "userId": user_id,
                                "jobId": job_id,
                                "searchId": search.get("_id") and str(search["_id"]),
                                "relevant": eval_result["relevant"],
                                "score": eval_result["score"],
                                "confidence": eval_result["confidence"],
                                "reason": eval_result["reason"],
                                "matchingSkills": eval_result["matchingSkills"],
                                "missingRequirements": eval_result["missingRequirements"],
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                            })

                            score_emoji = "✅" if eval_result["relevant"] else "❌"
                            await log("success" if eval_result["relevant"] else "warn",
                                      f"[AI] Relevance score: {eval_result['score']} — {score_emoji} {eval_result['reason'][:100]}")

                            if not eval_result["relevant"] or eval_result["score"] < ai_threshold:
                                await log("info", "[AI] Decision: NOT RELEVANT — skipping")
                                await db.applications.insert_one({
                                    "userId": user_id, "jobId": job_id,
                                    "searchId": search.get("_id") and str(search["_id"]),
                                    "roleKey": role_key, "runId": run_id,
                                    "status": "SKIPPED",
                                    "matchScore": eval_result["score"],
                                    "aiReason": eval_result["reason"],
                                    "recruiterEmail": email,
                                    "mode": mode,
                                    "createdAt": datetime.now(timezone.utc).isoformat(),
                                })
                                await db.automationruns.update_one(
                                    {"_id": ObjectId(run_id)},
                                    {"$inc": {"skippedCount": 1, "jobsEvaluated": 1}},
                                )
                                continue

                            await db.automationruns.update_one(
                                {"_id": ObjectId(run_id)},
                                {"$inc": {"relevantCount": 1, "jobsEvaluated": 1}},
                            )

                            resume_to_use = resume_path
                            if customize and resume:
                                await log("info", "[RESUME] Customizing resume for this job…")
                                from app.services.ai_service import customize_resume
                                custom = customize_resume(
                                    resume_text=resume.get("extractedText", ""),
                                    job_description=text,
                                    job_title=role.get("title", ""),
                                    candidate=profile,
                                )
                                ver_result = await db.resumeversions.insert_one({
                                    "userId": user_id,
                                    "resumeId": str(resume["_id"]),
                                    "label": f"Tailored — {role.get('title', '')}",
                                    "jobId": job_id,
                                    "jobTitle": role.get("title", ""),
                                    "createdBy": "ai",
                                    "tailoredText": custom["tailoredText"],
                                    "summaryOfChanges": custom["summaryOfChanges"],
                                    "createdAt": datetime.now(timezone.utc).isoformat(),
                                })
                                resume_version_id = str(ver_result.inserted_id)
                                await log("success", "[RESUME] Tailored resume prepared")
                            else:
                                resume_version_id = None

                            from app.services.ai_service import generate_application_message
                            message = generate_application_message(
                                candidate=profile,
                                job_title=role.get("title", ""),
                                company="",
                                recruiter_name="",
                                description=text,
                                matching_skills=eval_result.get("matchingSkills", []),
                            )

                            subject = (
                                f"{role.get('title', 'Position')} | "
                                f"{profile.get('fullName', 'Applicant')} | "
                                f"{profile.get('experience', '')} | "
                                f"{profile.get('workAuthorization', '')} | Immediate"
                            )

                            app_data = {
                                "userId": user_id,
                                "jobId": job_id,
                                "searchId": search.get("_id") and str(search["_id"]),
                                "roleKey": role_key,
                                "runId": run_id,
                                "status": "PREPARED",
                                "matchScore": eval_result["score"],
                                "aiReason": eval_result["reason"],
                                "emailSubject": subject,
                                "emailBody": message,
                                "recruiterEmail": email,
                                "ccEmails": search.get("ccEmails", []),
                                "bccEmails": search.get("bccEmails", []),
                                "resumeVersionId": resume_version_id,
                                "resumePath": resume_to_use,
                                "pendingApproval": mode == "REVIEW",
                                "mode": mode,
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                            }

                            if mode == "TEST":
                                app_data["status"] = "PREPARED"
                                await log("info", "[TEST] Prepared application — not sent")
                                await db.applications.insert_one(app_data)
                            elif mode == "REVIEW":
                                app_data["status"] = "PREPARED"
                                app_data["pendingApproval"] = True
                                await log("info", "[REVIEW] Application prepared — awaiting approval")
                                await db.applications.insert_one(app_data)
                                await _notify_ws(user_id, {"type": "review_needed", "applicationId": "", "email": email})
                            else:
                                await log("info", "[EMAIL] Sending application…")
                                from app.services.email_adapter import send_application_email
                                result = send_application_email(
                                    to_email=email,
                                    subject=subject,
                                    body=message,
                                    resume_path=resume_to_use,
                                    cc_emails=search.get("ccEmails", []),
                                    bcc_emails=search.get("bccEmails", []),
                                    user_email=profile.get("email", ""),
                                )
                                if result["success"]:
                                    app_data["status"] = "EMAIL_SENT"
                                    app_data["sentAt"] = datetime.now(timezone.utc).isoformat()
                                    await log("success", f"[EMAIL] Application sent successfully to {email}")
                                else:
                                    app_data["status"] = "FAILED"
                                    app_data["error"] = result.get("error", "")
                                    await log("error", f"[EMAIL] Send failed: {result.get('error', '')}")

                                await db.applications.insert_one(app_data)

                            if app_data["status"] == "EMAIL_SENT":
                                global_sent += 1
                                role_sent += 1
                                await db.automationruns.update_one(
                                    {"_id": ObjectId(run_id)},
                                    {"$inc": {"applicationsSent": 1}},
                                )
                                await _notify_ws(user_id, {
                                    "type": "application_sent",
                                    "email": email,
                                    "total": global_sent,
                                })

                            await asyncio.sleep(search.get("sendingPacingMs", 4000) / 1000)

                    except Exception as e:
                        await log("error", f"[ERROR] Card processing error: {str(e)[:200]}")
                        await db.automationruns.update_one(
                            {"_id": ObjectId(run_id)},
                            {"$inc": {"failedCount": 1}},
                        )
                        continue

            except Exception as e:
                await log("error", f"[BROWSER] Automation error: {str(e)[:300]}")
                await update_run({
                    "status": "ERROR",
                    "error": str(e)[:500],
                    "finishedAt": datetime.now(timezone.utc).isoformat(),
                })
                return

        # Completed
        await update_run({
            "status": "COMPLETED",
            "finishedAt": datetime.now(timezone.utc).isoformat(),
            "stoppedReason": "All roles processed",
        })
        await log("success", "[AUTOMATION] All roles completed!")

    except asyncio.CancelledError:
        await log("info", "[AUTOMATION] Stopped by user")
        await update_run({"status": "STOPPED", "finishedAt": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        await log("error", f"[AUTOMATION] Fatal error: {str(e)[:300]}")
        await update_run({
            "status": "ERROR",
            "error": str(e)[:500],
            "finishedAt": datetime.now(timezone.utc).isoformat(),
        })
