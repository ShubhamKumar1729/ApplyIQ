"""Resume processing service."""
import re
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"[PDF extraction failed: {e}]"


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX."""
    try:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"[DOCX extraction failed: {e}]"


def extract_text(file_path: str) -> str:
    """Extract text based on file extension."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        # Try reading as text
        try:
            return path.read_text(errors="ignore")[:10000]
        except Exception:
            return "[Unsupported file type]"


def calculate_profile_completeness(profile: dict) -> int:
    """Calculate profile completeness percentage."""
    fields = {
        "fullName": 10, "email": 10, "phone": 10,
        "location": 5, "headline": 5, "linkedin": 5,
        "skills": 10, "experience": 15, "education": 10,
        "workAuthorization": 5, "availability": 5,
        "projects": 5, "github": 2, "portfolio": 3,
    }
    score = 0
    for field, weight in fields.items():
        val = profile.get(field)
        if val:
            if isinstance(val, list) and len(val) > 0:
                score += weight
            elif isinstance(val, str) and len(val.strip()) > 0:
                score += weight
    return min(score, 100)
