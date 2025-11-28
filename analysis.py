"""
SkillPath - Analysis / AI Logic (analysis.py)

- PDF -> Text extraction
- Resume parsing using OpenAI (v1+ client)
- Job matching (adds job platform search links)
- Automatic Roadmap PDF Generator with actionable skill improvement steps
- Unicode-safe (supports ✅ and other UTF-8 characters)
"""

import os
import json
import uuid
import re
import string
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not set. Create a .env file with OPENAI_API_KEY=sk-..."
    )

client = OpenAI(api_key=API_KEY)

# folders
ROADMAP_DIR = "roadmaps"
os.makedirs(ROADMAP_DIR, exist_ok=True)


# ---------------------------
# Helpers
# ---------------------------
def extract_json_substring(s):
    m = re.search(r"(\{(?:.|\s)*\}|\[(?:.|\s)*\])", s, re.S)
    return m.group(1) if m else None


def build_job_search_links(role):
    """Build public job search URLs for LinkedIn, Seek, Indeed."""
    try:
        import urllib.parse as _up
    except Exception:
        role_q = role.replace(" ", "+")
        return {
            "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={role_q}",
            "seek": f"https://www.seek.com.au/{role_q}-jobs",
            "indeed": f"https://www.indeed.com/jobs?q={role_q}",
        }
    q = _up.quote(role)
    seek_q = _up.quote(role.replace(" ", "-"))
    return {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={q}",
        "seek": f"https://www.seek.com.au/{seek_q}-jobs",
        "indeed": f"https://www.indeed.com/jobs?q={q}",
    }


def _sanitize_filename(s):
    allowed = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(c for c in s if c in allowed).strip().replace(" ", "_")


# ---------------------------
# PDF text extraction
# ---------------------------
def extract_text_from_pdf(path):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(path)
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception:
        pass

    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text_parts.append(t)
        text = "\n".join(text_parts).strip()
        if text:
            return text
    except Exception:
        pass

    return ""


# ---------------------------
# Resume Parsing (LLM)
# ---------------------------
def parse_resume(filepath):
    text = extract_text_from_pdf(filepath)
    if not text:
        return {"error": "Could not extract text from PDF."}

    prompt = (
        "You are a professional resume parser. Extract the following fields in valid JSON:\n"
        "- name (string)\n"
        "- contact_info (object with email / phone / linkedin optional)\n"
        "- education (list of objects: {institution, degree, start_year, end_year})\n"
        "- experience (list of objects: {title, company, start, end, bullets})\n"
        "- skills (list of strings)\n\n"
        "Return JSON ONLY and ensure it's parseable by json.loads().\n\n"
        "Resume Text:\n"
        f"{text}\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )
        content = response.choices[0].message.content
    except Exception as e:
        return {"error": "OpenAI request failed", "detail": str(e)}

    try:
        return json.loads(content)
    except Exception:
        substring = extract_json_substring(content)
        if substring:
            try:
                return json.loads(substring)
            except Exception:
                pass
        return {"error": "LLM returned invalid JSON", "raw": content}


# ---------------------------
# Job Matching (LLM)
# ---------------------------
def match_candidate(parsed):
    skills = parsed.get("skills", [])
    skill_text = ", ".join(map(str, skills)) if isinstance(skills, (list, tuple)) else str(skills)

    prompt = (
        f"Based on these skills:\n{skill_text}\n\n"
        "Recommend 5 job roles as a JSON list. Each item must include:\n"
        "- role (string)\n"
        "- match_score (number 0-100)\n"
        "- missing_skills (list of strings)\n"
        "- explanation (string)\n\n"
        "Return JSON only."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content
    except Exception as e:
        return {"error": "OpenAI request failed", "detail": str(e)}

    parsed_resp = None
    try:
        parsed_resp = json.loads(content)
    except Exception:
        substring = extract_json_substring(content)
        if substring:
            try:
                parsed_resp = json.loads(substring)
            except Exception:
                parsed_resp = None

    if parsed_resp is None:
        return {"error": "LLM returned invalid JSON for matches", "raw": content}

    if isinstance(parsed_resp, dict) and "matches" in parsed_resp:
        parsed_resp = parsed_resp["matches"]
    elif isinstance(parsed_resp, dict):
        parsed_resp = [parsed_resp]

    results = []
    for item in parsed_resp:
        if not isinstance(item, dict):
            continue
        role = item.get("role", "")
        links = build_job_search_links(role) if role else {}
        missing = item.get("missing_skills", []) or []
        if isinstance(missing, str):
            missing = [s.strip() for s in missing.split(",") if s.strip()]
        try:
            score = int(float(item.get("match_score", 0)))
        except Exception:
            score = 0

        results.append({
            "role": role,
            "match_score": score,
            "missing_skills": missing,
            "explanation": item.get("explanation", ""),
            "search_links": links
        })

    return results


# ---------------------------
# Build actionable steps automatically
# ---------------------------
def build_steps_for_role(match):
    role = match.get("role", "Unknown Role")
    score = match.get("match_score", 0)
    missing = match.get("missing_skills", [])

    steps = [f"Current Match Score: {score}%"]

    if missing:
        steps.append(f"Missing skills: {', '.join(missing)}")
        for skill in missing:
            steps.append(f"✅ Learn or improve your skill in {skill} (online courses / tutorials)")
            steps.append(f"✅ Build a small project using {skill} to gain practical experience")
    else:
        steps.append("All required skills are already matched!")

    steps += [
        "✅ Update your resume to highlight your newly acquired skills and projects",
        "✅ Add your projects to your portfolio or GitHub",
        "✅ Apply to similar roles using the job search links provided"
    ]

    return steps


# ---------------------------
# Unicode-safe PDF generator
# ---------------------------
def generate_roadmap(match):
    """
    Automatically generates a PDF with all steps included (supports Unicode)
    """
    # Fix: handle both 'role' and 'target_role'
    role = match.get("role") or match.get("target_role") or "Career Path"
    steps = build_steps_for_role(match)

    pdf_path = os.path.join(ROADMAP_DIR, f"{uuid.uuid4()}.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Use DejaVuSans for Unicode
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    if os.path.isfile(font_path):
        pdf.add_font("DejaVuSans", "", font_path, uni=True)
        base_font = "DejaVuSans"
    else:
        base_font = "Arial"

    # Title
    pdf.set_font(base_font, "", 16)
    pdf.cell(0, 10, "Career Roadmap", ln=True)

    # Role
    pdf.set_font(base_font, "", 14)
    pdf.ln(3)
    pdf.cell(0, 10, f"Target Role: {role}", ln=True)
    pdf.ln(5)

    # Steps
    pdf.set_font(base_font, "", 12)
    pdf.cell(0, 10, "Steps:", ln=True)
    pdf.ln(2)

    for s in steps:
        pdf.multi_cell(0, 8, s)
        pdf.ln(1)

    pdf.output(pdf_path)
    return pdf_path


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    example_parsed = {"skills": ["python", "sql", "excel"]}
    matches = match_candidate(example_parsed)

    for m in matches:
        pdf_path = generate_roadmap(m)
        print(f"Generated PDF for {m['role']}: {pdf_path}")
