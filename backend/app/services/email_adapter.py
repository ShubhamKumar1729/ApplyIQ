"""Email adapter — wraps the EXISTING yagmail email sender."""
import sys, time, re
from pathlib import Path

# Add project root to path so we can import existing modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.email_sender import send_email as _existing_send_email
from core.tracker import load_sent_cache, already_sent, save_sent
from core.filters import filter_recruiter_emails, should_send_to_post
from utils.helpers import extract_emails, normalize_email, clean


def _clean_jd(post_text: str) -> str:
    """Clean job description text of UI junk."""
    junk = {
        "like", "comment", "repost", "send", "follow", "connect",
        "join", "more", "privacy & terms", "help center",
    }
    lines = []
    for line in post_text.split("\n"):
        line = line.strip()
        if not line or len(line) < 3:
            continue
        if line.lower() in junk:
            continue
        if re.match(r"^\d+\s*(reaction|comment)", line.lower()):
            continue
        if re.match(r"^\d+[mh]\s*[•·]?", line):
            continue
        lines.append(line)
    text = "\n".join(lines)
    if len(text) > 1200:
        text = text[:1200].rsplit("\n", 1)[0] + "\n..."
    return text.strip()


def send_application_email(
    to_email: str,
    subject: str,
    body: str,
    resume_path: str,
    cc_emails: list = None,
    bcc_emails: list = None,
    post_link: str = "",
    role_name: str = "",
    recruiter_name: str = "",
    post_text: str = "",
    user_email: str = "",
) -> dict:
    """
    Send an application email using the EXISTING email system.
    Returns {success: bool, error: str}
    """
    # Ensure sent cache is loaded
    try:
        load_sent_cache()
    except Exception:
        pass

    # Validate
    if not to_email or "@" not in to_email:
        return {"success": False, "error": "Invalid email address"}

    # Check not sending to self
    if user_email and normalize_email(to_email) == normalize_email(user_email):
        return {"success": False, "error": "Cannot send to self"}

    # Filter CC/BCC
    filtered_cc = [normalize_email(e) for e in (cc_emails or [])
                   if normalize_email(e) != normalize_email(to_email)]
    filtered_bcc = [normalize_email(e) for e in (bcc_emails or [])
                    if normalize_email(e) != normalize_email(to_email)
                    and normalize_email(e) not in filtered_cc]

    # Build role dict for existing sender
    role = {
        "name": role_name or "Position",
        "skills": "",
        "search": "",
    }

    try:
        success = _existing_send_email(
            to_email=to_email,
            role=role,
            post_text=post_text or body,
            post_link=post_link,
            resume_path=Path(resume_path),
            recruiter_name=recruiter_name,
        )
        if success:
            return {"success": True, "error": ""}
        return {"success": False, "error": "Email send returned False"}
    except Exception as e:
        return {"success": False, "error": str(e)[:300]}


def validate_recruiter_email(email: str) -> bool:
    """Validate email using existing filter system."""
    valid = filter_recruiter_emails([email])
    return len(valid) > 0


def extract_and_validate_emails(text: str) -> list:
    """Extract and validate emails from text using existing system."""
    raw = extract_emails(text)
    return filter_recruiter_emails(raw)
