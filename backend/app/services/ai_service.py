"""Groq AI service — relevance evaluation & resume customization."""
import json, re, os
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

client = None

def _get_client() -> Groq:
    global client
    if client is None:
        key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        if not key:
            raise ValueError("GROQ_API_KEY not configured")
        client = Groq(api_key=key)
    return client


def _chat(system: str, user: str, temperature: float = 0.3) -> str:
    c = _get_client()
    resp = c.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=4096,
    )
    return resp.choices[0].message.content or ""


# ── Relevance Evaluation ────────────────────────────────────
def evaluate_relevance(
    candidate: dict,
    role: dict,
    job_title: str,
    company: str,
    location: str,
    description: str,
    resume_text: str = "",
) -> dict:
    """Ask Groq to evaluate job relevance. Returns structured dict."""
    system = """You are an expert job-matching AI. Evaluate if a job is relevant for a candidate.
Return ONLY valid JSON with this exact structure:
{
  "relevant": true/false,
  "score": 0-100,
  "confidence": "high"/"medium"/"low",
  "reason": "brief explanation",
  "matchingSkills": ["skill1", "skill2"],
  "missingRequirements": ["req1"]
}
Do NOT reject just because it's a staffing company or recruiter post.
Do NOT reject different experience levels.
Reject only: genuinely different role, non-genuine job, or clearly mismatched."""

    user = f"""Candidate Profile:
Name: {candidate.get('fullName', 'N/A')}
Skills: {', '.join(candidate.get('skills', [])) or 'N/A'}
Experience: {candidate.get('experience', 'N/A')}
Work Auth: {candidate.get('workAuthorization', 'N/A')}
Location: {candidate.get('location', 'N/A')}

Target Role: {role.get('title', 'N/A')}
Role Skills: {role.get('query', 'N/A')}

Job Details:
Title: {job_title}
Company: {company}
Location: {location}
Description:
{description[:3000]}

Resume Excerpt:
{resume_text[:1500]}"""

    try:
        raw = _chat(system, user, temperature=0.1)
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            result = json.loads(json_match.group())
            # Ensure all fields exist
            return {
                "relevant": bool(result.get("relevant", False)),
                "score": int(result.get("score", 0)),
                "confidence": str(result.get("confidence", "medium")),
                "reason": str(result.get("reason", "")),
                "matchingSkills": list(result.get("matchingSkills", [])),
                "missingRequirements": list(result.get("missingRequirements", [])),
            }
        return {"relevant": False, "score": 0, "confidence": "low",
                "reason": "Failed to parse AI response", "matchingSkills": [], "missingRequirements": []}
    except Exception as e:
        return {"relevant": False, "score": 0, "confidence": "low",
                "reason": f"AI evaluation failed: {str(e)[:200]}", "matchingSkills": [], "missingRequirements": []}


# ── Resume Customization ────────────────────────────────────
def customize_resume(
    resume_text: str,
    job_description: str,
    job_title: str,
    candidate: dict,
) -> dict:
    """Use Groq to tailor resume to job. Returns {tailoredText, summaryOfChanges}."""
    system = """You are an expert resume writer. Customize the candidate's resume for a specific job.
RULES:
- ONLY reorder, rephrase, or emphasize EXISTING information
- NEVER invent skills, experience, companies, projects, certifications, degrees, or achievements
- Improve wording and structure
- Highlight relevant experience for the target role
- Keep it truthful and professional

Return ONLY valid JSON:
{
  "tailoredText": "the customized resume text",
  "summaryOfChanges": "brief summary of what was changed"
}"""

    user = f"""Target Job: {job_title}

Job Description:
{job_description[:3000]}

Candidate Profile:
{json.dumps({k: v for k, v in candidate.items() if v}, indent=2)[:1000]}

Original Resume:
{resume_text[:4000]}"""

    try:
        raw = _chat(system, user, temperature=0.4)
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            result = json.loads(json_match.group())
            return {
                "tailoredText": str(result.get("tailoredText", resume_text)),
                "summaryOfChanges": str(result.get("summaryOfChanges", "")),
            }
        return {"tailoredText": resume_text, "summaryOfChanges": "Could not parse AI response"}
    except Exception as e:
        return {"tailoredText": resume_text, "summaryOfChanges": f"Customization failed: {str(e)[:200]}"}


# ── Application Message Generation ──────────────────────────
def generate_application_message(
    candidate: dict,
    job_title: str,
    company: str,
    recruiter_name: str,
    description: str,
    matching_skills: list,
) -> str:
    """Generate personalized application email body."""
    system = """You are a professional job application writer. Write a concise, personalized application email.
RULES:
- Address the recruiter by name (or "Hiring Manager" if unknown)
- Mention the specific job title and company
- Highlight relevant skills that match the job
- Keep it professional, concise, and genuine
- Do NOT invent any information
- Include a call to action
- Maximum 250 words"""

    greeting_name = recruiter_name or "Hiring Manager"
    user = f"""Write an application email for:

Candidate: {candidate.get('fullName', 'N/A')}
Experience: {candidate.get('experience', 'N/A')}
Skills: {', '.join(matching_skills) or ', '.join(candidate.get('skills', []))}
Location: {candidate.get('location', 'N/A')}

Job: {job_title} at {company}
Recruiter: {greeting_name}

Key job requirements:
{description[:1500]}"""

    try:
        return _chat(system, user, temperature=0.5)
    except Exception:
        # Fallback template
        skills_str = ", ".join(matching_skills) if matching_skills else ", ".join(candidate.get("skills", []))
        return (
            f"Dear {greeting_name},\n\n"
            f"I am writing to express my interest in the {job_title} position at {company}. "
            f"With my experience in {skills_str}, I believe I would be a strong fit for this role.\n\n"
            f"I have attached my resume for your review. I would welcome the opportunity to discuss "
            f"how my skills align with your team's needs.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best regards,\n{candidate.get('fullName', '')}"
        )
