"""
Matching engine to score and categorize job postings based on Saikumar's resume.
"""
import re
from config import PROFILE, MIN_SCORE_THRESHOLD

def evaluate_job(title: str, description: str, location: str, tags: list = None) -> dict:
    """
    Evaluates a job and returns scoring details:
    {
        "eligible": bool,
        "match_score": int,
        "category": str,
        "matched_skills": list,
        "location_ok": bool
    }
    """
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    loc_lower = location.lower() if location else ""
    tags_str = " ".join([str(t).lower() for t in (tags or [])])
    full_text = f"{title_lower} {tags_str} {desc_lower}"

    # Negative title filter (roles completely outside tech testing/data)
    unrelated_roles = [
        r'\b(sales|recruiter|hr|talent|marketing\s*manager|copywriter|legal|nurse|receptionist|account\s*exec|graphic\s*designer|frontend\s*react\s*developer|mobile\s*flutter)\b'
    ]
    if any(re.search(pat, title_lower) for pat in unrelated_roles):
        return {"eligible": False, "match_score": 0}

    # Location check
    location_ok = True
    for restricted in PROFILE["location_preferences"]["restricted"]:
        if restricted in loc_lower:
            location_ok = False
            break

    # Title score
    title_score = 0
    if any(k in title_lower for k in ["etl", "data quality", "data test", "data qa", "dwh test", "validation"]):
        title_score = 60
    elif any(k in title_lower for k in ["qa automation", "sdet", "test automation", "qa engineer", "quality engineer", "software test"]):
        title_score = 45
    elif any(k in title_lower for k in ["data analyst", "bi analyst", "data engineer", "analytics engineer"]):
        title_score = 25
    elif any(k in title_lower for k in ["qa", "test", "tester"]):
        title_score = 35

    # Skill scoring
    skill_score = 0
    matched_skills = []
    for skill, weight in PROFILE["must_have_skills"].items():
        if re.search(r'\b' + re.escape(skill) + r'\b', full_text):
            skill_score += weight
            matched_skills.append(skill)

    # Max skill score cap at 50
    total_score = title_score + min(skill_score, 50)

    # If title wasn't an explicit QA/Data title, require at least SQL or Python or QA skill
    if title_score == 0 and not any(s in matched_skills for s in ["sql", "python", "etl", "data quality"]):
        return {"eligible": False, "match_score": 0}

    eligible = (total_score >= MIN_SCORE_THRESHOLD) and location_ok

    # Categorization
    if any(k in title_lower for k in ["etl", "data quality", "data test", "validation"]) or ("data quality" in matched_skills and "sql" in matched_skills):
        category = "Direct Fit: ETL & Data Quality Testing"
    elif any(k in title_lower for k in ["qa", "test", "sdet", "quality assurance"]):
        category = "Strong Fit: QA Automation & Test Engineering"
    elif any(k in title_lower for k in ["data analyst", "bi", "analytics", "power bi"]):
        category = "Analytics & BI: SQL / Data Validation"
    else:
        category = "Data & Platform Engineering (Python/SQL)"

    return {
        "eligible": eligible,
        "match_score": min(total_score, 100),
        "category": category,
        "matched_skills": sorted(list(set(matched_skills))),
        "location_ok": location_ok
    }
