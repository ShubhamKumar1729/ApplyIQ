import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── MongoDB ──────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB  = os.getenv("MONGODB_DB", "applyiq")

# ── Auth ─────────────────────────────────────────────────────
AUTH_SECRET     = os.getenv("AUTH_SECRET", "change-me-in-production-applyiq-2024")
AUTH_ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

# ── Groq AI ──────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
AI_RELEVANCE_THRESHOLD = int(os.getenv("AI_RELEVANCE_THRESHOLD", "70"))

# ── Upload ───────────────────────────────────────────────────
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESUME_DIR = UPLOAD_DIR / "resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10MB

# ── Existing project integration ─────────────────────────────
GMAIL_ID           = os.getenv("GMAIL_ID", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
LINKEDIN_PROFILE_DIR = os.getenv("LINKEDIN_PROFILE_DIR", str(BASE_DIR / "linkedin_profile_data"))

# ── Automation ───────────────────────────────────────────────
AUTOMATION_RATE_LIMIT_MS = int(os.getenv("AUTOMATION_RATE_LIMIT_MS", "4000"))
AUTOMATION_CONCURRENCY   = int(os.getenv("AUTOMATION_CONCURRENCY", "1"))
MAX_EMAILS_PER_POST      = int(os.getenv("MAX_EMAILS_PER_POST", "5"))
SCROLL_ROUNDS            = int(os.getenv("SCROLL_ROUNDS", "8"))

# ── Email filtering (from existing project) ──────────────────
BAD_EMAIL_PREFIXES = {
    "noreply", "no-reply", "donotreply", "do-not-reply",
    "admin", "support", "help", "info", "contact",
    "sales", "marketing", "privacy", "security",
    "abuse", "postmaster", "mailer-daemon",
}
BAD_EMAIL_DOMAINS = {"linkedin.com", "example.com", "test.com"}
