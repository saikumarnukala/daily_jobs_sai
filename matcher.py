"""
Matching engine to score and categorize job postings based on Saikumar's resume:
Scope:
  - ETL Test Engineer
  - Data Quality Engineer
  - SDET in Data
  - Software Test Engineer in Data
  - ETL Database Testing
Location:
  - Remote working from India OR Worldwide / Global Remote (no timing/shift issues)
"""
import re
from config import PROFILE, MIN_SCORE_THRESHOLD

def is_remote_india_or_worldwide(location: str) -> bool:
    """
    Validates whether candidate in India can work remotely for this role.
    Allowed:
      - Explicitly in India (e.g. Bengaluru, Remote India, etc.)
      - Worldwide / Anywhere / Global / Work from anywhere
      - Generic 'Remote' without foreign country exclusions
    Rejected:
      - Country-locked to US, Canada, UK, Europe, Australia, etc.
    """
    if not location:
        return True
    loc_clean = location.lower().strip()

    rules = PROFILE.get("location_rules", {})
    india_indicators = rules.get("india_indicators", [])
    worldwide_indicators = rules.get("worldwide_indicators", [])
    foreign_restricted = rules.get("foreign_restricted", [])

    # 1. India specific locations
    if any(t in loc_clean for t in india_indicators):
        return True

    # 2. Worldwide / Global
    if any(t in loc_clean for t in worldwide_indicators):
        return True

    # 3. Open 'Remote' without foreign restrictions
    if loc_clean in ["remote", "any", "all", "work from home"]:
        return True

    # 4. If it mentions foreign regions, reject unless worldwide/India was found
    if any(r in loc_clean for r in foreign_restricted):
        return False

    # Default fallback for ambiguous multi-city locations
    return False

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

    # 1. Negative Filter: Reject completely unrelated roles
    unrelated_roles = [
        r'\b(sales|recruiter|hr|talent|marketing\s*manager|copywriter|legal|nurse|receptionist|account\s*exec|graphic\s*designer|frontend\s*react\s*developer|mobile\s*flutter|ios\s*developer|android\s*developer)\b'
    ]
    if any(re.search(pat, title_lower) for pat in unrelated_roles):
        return {"eligible": False, "match_score": 0}

    # 2. Location Eligibility Filter (India or Worldwide Remote)
    location_ok = is_remote_india_or_worldwide(location)
    if not location_ok:
        return {"eligible": False, "match_score": 0, "location_ok": False}

    # 3. Check Primary In-Scope Titles:
    # (ETL Test Engineer, Data Quality Engineer, SDET in Data, Software Test Engineer in Data, ETL Database Testing)
    primary_title_match = False
    primary_category = None

    for pat in PROFILE.get("in_scope_title_patterns", []):
        if re.search(pat, title_lower):
            primary_title_match = True
            break

    # Determine specific category
    if re.search(r'\b(etl\s*(?:test|testing|qa|tester|validation)|etl\s*(?:&|and)?\s*database)\b', title_lower):
        primary_category = "ETL Test Engineer"
    elif re.search(r'\b(data\s*quality\s*(?:engineer|analyst|qa|tester|specialist|lead))\b', title_lower):
        primary_category = "Data Quality Engineer"
    elif re.search(r'\b(sdet\b.*?\b(?:data|pipeline|warehouse|platform|analytics|etl|sql)|(?:data|pipeline|warehouse)\b.*?\bsdet\b)\b', title_lower):
        primary_category = "SDET in Data"
    elif re.search(r'\b(data\s*(?:qa|test|testing|validation)|software\s*test\s*engineer\b.*?\b(?:data|etl|database|warehouse))\b', title_lower):
        primary_category = "Software Test Engineer in Data"
    elif re.search(r'\b(database\s*(?:test|testing|qa|tester)|sql\s*(?:test|testing|qa))\b', title_lower):
        primary_category = "ETL Database Testing"

    # 4. Secondary Titles: General QA / SDET / Data roles
    secondary_title_match = False
    if not primary_title_match:
        for pat in PROFILE.get("secondary_title_patterns", []):
            if re.search(pat, title_lower):
                secondary_title_match = True
                break

    # 5. Extract and Score Skills
    matched_skills = []
    skill_score = 0
    for skill, weight in PROFILE.get("must_have_skills", {}).items():
        if re.search(r'\b' + re.escape(skill) + r'\b', full_text):
            skill_score += weight
            matched_skills.append(skill)

    # Has strong data testing skills in description?
    has_data_testing_skills = any(s in matched_skills for s in [
        "etl", "data quality", "data validation", "data warehouse", "dwh", "database testing", "source to target"
    ]) and ("sql" in matched_skills or "python" in matched_skills or "database" in matched_skills)

    # Title Scoring logic
    if primary_title_match:
        title_score = 65
    elif secondary_title_match and has_data_testing_skills:
        # General QA / SDET / Data role that requires ETL/Data Quality/Database testing
        title_score = 45
        if not primary_category:
            if "sdet" in title_lower:
                primary_category = "SDET in Data"
            elif any(k in title_lower for k in ["qa", "test", "quality"]):
                primary_category = "Software Test Engineer in Data"
            else:
                primary_category = "ETL Database Testing"
    else:
        # Title is not in scope or generic QA without any data scope
        return {"eligible": False, "match_score": 0}

    total_score = title_score + min(skill_score, 40)

    # 6. Final Threshold Gate
    eligible = (total_score >= MIN_SCORE_THRESHOLD) and location_ok

    category = primary_category or "Data Quality & ETL Testing"

    return {
        "eligible": eligible,
        "match_score": min(total_score, 100),
        "category": category,
        "matched_skills": sorted(list(set(matched_skills))),
        "location_ok": location_ok
    }
