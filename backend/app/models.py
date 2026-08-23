"""ApplyIQ — All Pydantic models (request/response schemas)."""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


# ═══════════════════════ ENUMS ══════════════════════════════
class ApplicationStatus(str, Enum):
    AI_MATCHED = "AI_MATCHED"
    PREPARED = "PREPARED"
    EMAIL_SENT = "EMAIL_SENT"
    APPLIED = "APPLIED"
    RESPONSE = "RESPONSE"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ApplicationMode(str, Enum):
    AUTO_APPLY = "AUTO_APPLY"
    REVIEW = "REVIEW"
    TEST = "TEST"


class ResumeStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class LogLevel(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    SUCCESS = "success"


class NotificationType(str, Enum):
    AUTOMATION_STARTED = "AUTOMATION_STARTED"
    AUTOMATION_PAUSED = "AUTOMATION_PAUSED"
    AUTOMATION_RESUMED = "AUTOMATION_RESUMED"
    AUTOMATION_COMPLETED = "AUTOMATION_COMPLETED"
    AUTOMATION_STOPPED = "AUTOMATION_STOPPED"
    APPLICATION_SENT = "APPLICATION_SENT"
    APPLICATION_FAILED = "APPLICATION_FAILED"
    LIMIT_REACHED = "LIMIT_REACHED"
    ERROR = "ERROR"
    RESUME_PROCESSED = "RESUME_PROCESSED"
    REVIEW_NEEDED = "REVIEW_NEEDED"
    GENERAL = "GENERAL"


class WorkplaceType(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


# ═══════════════════════ AUTH ═══════════════════════════════
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ═══════════════════════ PROFILE ════════════════════════════
class ProfileUpdate(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = ""
    relocation: Optional[str] = None
    workAuthorization: Optional[str] = None
    availability: Optional[str] = None
    rate: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    headline: Optional[str] = None
    skills: Optional[List[str]] = []
    experience: Optional[List[dict]] = []
    education: Optional[List[dict]] = []
    projects: Optional[List[dict]] = []
    certifications: Optional[List[dict]] = []
    preferredLocations: Optional[List[str]] = []
    preferredWorkplaceTypes: Optional[List[str]] = []


class ProfileResponse(BaseModel):
    id: str
    userId: str
    fullName: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""
    relocation: Optional[str] = ""
    workAuthorization: Optional[str] = ""
    availability: Optional[str] = ""
    rate: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    headline: Optional[str] = ""
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []
    projects: List[dict] = []
    certifications: List[dict] = []
    preferredLocations: List[str] = []
    preferredWorkplaceTypes: List[str] = []
    completeness: int = 0
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


# ═══════════════════════ RESUME ═════════════════════════════
class ResumeResponse(BaseModel):
    id: str
    userId: str
    filename: str
    originalName: str
    mimeType: str
    sizeBytes: int
    storageKey: str
    status: str = "READY"
    isDefault: bool = False
    extractedText: Optional[str] = ""
    createdAt: Optional[str] = None


# ═══════════════════════ RESUME VERSION ═════════════════════
class ResumeVersionCreate(BaseModel):
    resumeId: str
    jobId: Optional[str] = None
    jobTitle: Optional[str] = ""
    tailoredText: str
    summaryOfChanges: str = ""
    createdBy: str = "ai"  # "ai" or "user"


class ResumeVersionResponse(BaseModel):
    id: str
    userId: str
    resumeId: str
    label: str
    jobId: Optional[str] = None
    jobTitle: Optional[str] = ""
    createdBy: str = "ai"
    tailoredText: str
    summaryOfChanges: str = ""
    createdAt: Optional[str] = None


# ═══════════════════════ ROLE CONFIG ════════════════════════
class RoleConfig(BaseModel):
    key: str = ""
    title: str
    query: str
    location: Optional[str] = ""
    maxApplications: int = 15
    resumeId: Optional[str] = None
    enabled: bool = True
    workplaceType: Optional[str] = None
    experienceLevel: Optional[str] = None
    employmentType: Optional[str] = None
    datePosted: Optional[str] = "LAST_24H"
    keywords: List[str] = []
    requiredKeywords: List[str] = []
    excludedKeywords: List[str] = []
    titleInclude: List[str] = []
    titleExclude: List[str] = []
    companyInclude: List[str] = []
    companyExclude: List[str] = []
    industry: List[str] = []
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    currency: str = "USD"


# ═══════════════════════ JOB SEARCH ═════════════════════════
class JobSearchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    roles: List[RoleConfig] = []
    applicationMode: ApplicationMode = ApplicationMode.AUTO_APPLY
    customizeResume: bool = False
    aiThreshold: int = Field(default=70, ge=0, le=100)
    globalMaxApplications: int = Field(default=50, ge=1, le=500)
    ccEmails: List[str] = []
    bccEmails: List[str] = []
    schedule: Optional[dict] = None


class JobSearchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[List[RoleConfig]] = None
    applicationMode: Optional[ApplicationMode] = None
    customizeResume: Optional[bool] = None
    aiThreshold: Optional[int] = Field(default=None, ge=0, le=100)
    globalMaxApplications: Optional[int] = Field(default=None, ge=1, le=500)
    ccEmails: Optional[List[str]] = None
    bccEmails: Optional[List[str]] = None
    schedule: Optional[dict] = None
    paused: Optional[bool] = None
    archived: Optional[bool] = None


class JobSearchResponse(BaseModel):
    id: str
    userId: str
    name: str
    description: str = ""
    roles: List[RoleConfig] = []
    applicationMode: str = "AUTO_APPLY"
    customizeResume: bool = False
    aiThreshold: int = 70
    globalMaxApplications: int = 50
    ccEmails: List[str] = []
    bccEmails: List[str] = []
    schedule: Optional[dict] = None
    paused: bool = False
    archived: bool = False
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


# ═══════════════════════ JOB ════════════════════════════════
class JobResponse(BaseModel):
    id: str
    userId: str
    searchId: Optional[str] = None
    source: str = "linkedin"
    sourceId: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    url: str = ""
    postedDate: Optional[str] = None
    employmentType: str = ""
    workplaceType: str = ""
    salaryRange: str = ""
    recruiterEmail: str = ""
    recruiterName: str = ""
    raw: dict = {}
    createdAt: Optional[str] = None


# ═══════════════════════ AI EVALUATION ══════════════════════
class AIEvaluationResponse(BaseModel):
    id: str
    userId: str
    jobId: str
    searchId: Optional[str] = None
    relevant: bool = False
    score: int = 0
    confidence: str = ""
    reason: str = ""
    matchingSkills: List[str] = []
    missingRequirements: List[str] = []
    createdAt: Optional[str] = None


class FeedbackRequest(BaseModel):
    evaluationId: str
    helpful: bool
    comment: Optional[str] = ""


# ═══════════════════════ APPLICATION ════════════════════════
class ApplicationResponse(BaseModel):
    id: str
    userId: str
    jobId: Optional[str] = None
    searchId: Optional[str] = None
    roleKey: str = ""
    runId: Optional[str] = None
    status: str = "PREPARED"
    matchScore: int = 0
    aiReason: str = ""
    emailSubject: str = ""
    emailBody: str = ""
    recruiterEmail: str = ""
    ccEmails: List[str] = []
    bccEmails: List[str] = []
    resumeVersionId: Optional[str] = None
    sentAt: Optional[str] = None
    pendingApproval: bool = False
    mode: str = "AUTO_APPLY"
    notes: str = ""
    feedback: Optional[dict] = None
    error: str = ""
    createdAt: Optional[str] = None
    job: Optional[dict] = None


class ApplicationApprove(BaseModel):
    approved: bool
    notes: Optional[str] = ""


# ═══════════════════════ AUTOMATION ═════════════════════════
class AutomationStartRequest(BaseModel):
    searchId: str


class AutomationRunResponse(BaseModel):
    id: str
    userId: str
    searchId: str
    status: str = "PENDING"
    jobsFound: int = 0
    jobsEvaluated: int = 0
    relevantCount: int = 0
    applicationsSent: int = 0
    skippedCount: int = 0
    failedCount: int = 0
    currentRoleKey: str = ""
    currentJobId: str = ""
    currentJobTitle: str = ""
    globalMax: int = 50
    startedAt: Optional[str] = None
    finishedAt: Optional[str] = None
    error: str = ""
    createdAt: Optional[str] = None


class AutomationLogEntry(BaseModel):
    id: Optional[str] = None
    runId: str = ""
    jobId: str = ""
    level: str = "info"
    message: str = ""
    createdAt: Optional[str] = None


# ═══════════════════════ NOTIFICATION ═══════════════════════
class NotificationResponse(BaseModel):
    id: str
    userId: str
    type: str = "GENERAL"
    title: str = ""
    message: str = ""
    link: str = ""
    read: bool = False
    createdAt: Optional[str] = None


# ═══════════════════════ SETTINGS ═══════════════════════════
class SettingsUpdate(BaseModel):
    theme: Optional[str] = None  # "light", "dark", "system"
    defaultApplicationMode: Optional[str] = None
    defaultAiThreshold: Optional[int] = None
    defaultMaxApplications: Optional[int] = None
    defaultCustomizeResume: Optional[bool] = None
    defaultResumeId: Optional[str] = None
    sendingPacingMs: Optional[int] = None
    dataRetentionDays: Optional[int] = None


class SettingsResponse(BaseModel):
    id: str
    userId: str
    theme: str = "system"
    defaultApplicationMode: str = "AUTO_APPLY"
    defaultAiThreshold: int = 70
    defaultMaxApplications: int = 50
    defaultCustomizeResume: bool = False
    defaultResumeId: str = ""
    sendingPacingMs: int = 4000
    dataRetentionDays: int = 90


# ═══════════════════════ DASHBOARD ══════════════════════════
class DashboardStats(BaseModel):
    totalApplications: int = 0
    applicationsSent: int = 0
    relevantJobs: int = 0
    responseRate: float = 0.0
    activeSearches: int = 0
    recentRuns: List[dict] = []
    recentApplications: List[dict] = []
    profileCompleteness: int = 0
    liveAutomation: Optional[dict] = None


# ═══════════════════════ ANALYTICS ══════════════════════════
class AnalyticsData(BaseModel):
    applicationsOverTime: List[dict] = []
    statusFunnel: dict = {}
    perSearchPerformance: List[dict] = []
    perRolePerformance: List[dict] = []
    totalApplications: int = 0
    totalSent: int = 0
    totalResponses: int = 0
    totalInterviews: int = 0
    totalOffers: int = 0
    totalRejected: int = 0


# ═══════════════════════ API RESPONSE ═══════════════════════
class APIResponse(BaseModel):
    ok: bool = True
    data: Any = None
    error: Optional[dict] = None
