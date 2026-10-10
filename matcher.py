"""
Matching engine to score and categorize job postings based on Saikumar's resume:
Strict Search Scope:
  - TITLE MUST be explicitly in scope:
      1. ETL Test Engineer (ETL QA / Tester / Validation)
      2. Data Quality Engineer (Data Quality Analyst / QA / Tester)
      3. SDET in Data (Software Development Engineer in Test - Data / Database / Automation)
      4. Software Test Engineer in Data (Data QA Engineer / Data Test Engineer)
      5. ETL Database Testing (Database Test Engineer / SQL Test Engineer / Database QA)
Location:
  - Remote working from India OR Worldwide / Global Remote (no timing/shift issues)
"""
import re
from config import PROFILE, MIN_SCORE_THRESHOLD

def is_remote_india_or_worldwide(location: str) -> bool:
    """
    Validates whether candidate in India can work remotely for this role.
    Allowed:
      - Explicitly in India (e.g. Bengaluru, Bangalore, Remote India, etc.)
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

    return False

def is_title_in_scope(title: str) -> tuple[bool, str]:
    """
    Strictly validates the job TITLE only.
    Rejects generic roles like 'Data Analyst' or 'Data Engineer'.
    Title MUST be explicitly QA / Test / SDET / Data Quality / ETL Testing.
    """
    t = title.lower().strip()

    # Must contain test / qa / sdet / quality / validation in the TITLE itself
    must_have_test_terms = ['test', 'qa', 'sdet', 'quality', 'tester', 'validation']
    if not any(term in t for term in must_have_test_terms):
        return False, ""

    # Reject non-software, hardware, cider, food, manual evaluator/annotation roles
    unrelated_roles = [
        'dispense', 'technician', 'fire tester', 'civil', 'cider', 'hardware', 
        'medical', 'nurse', 'qa evaluator', 'image qa', 'annotation', 'evaluator',
        'quality assurance representative', 'quality control technician', 'call center'
    ]
    if any(un in t for un in unrelated_roles):
        return False, ""

    # 1. ETL Test Engineer / ETL QA
    if re.search(r'\b(etl\s*(?:test|testing|qa|tester|validation|engineer))\b', t):
        return True, "ETL Test Engineer"

    # 2. Data Quality Engineer / Analyst
    if re.search(r'\b(data\s*quality\s*(?:engineer|analyst|qa|tester|specialist|lead))\b', t):
        return True, "Data Quality Engineer"

    # 3. SDET in Data / Database Automation
    if re.search(r'\b(sdet|software\s*development\s*engineer\s*in\s*test)\b.*?\b(database|data|etl|platform|automation|backend)\b', t) or \
       re.search(r'\b(database|data|etl)\b.*?\b(sdet|software\s*development\s*engineer\s*in\s*test)\b', t):
        return True, "SDET in Data"

    # 4. ETL Database Testing / Database Test Engineer / SQL QA
    if re.search(r'\b(database\s*(?:test|testing|qa|tester|automation)|sql\s*(?:test|testing|qa|tester))\b', t) or \
       re.search(r'\b(etl\s*(?:&|and)?\s*database\s*(?:test|testing|qa))\b', t):
        return True, "ETL Database Testing"

    # 5. Software Test Engineer in Data / Data QA Engineer
    if re.search(r'\b(data\s*(?:qa|test|testing|validation)(?:\s*automation)?\s*(?:engineer|analyst|lead|specialist))\b', t) or \
       re.search(r'\b(?:software\s*test|qa)\s*(?:engineer|analyst|lead|specialist)\b.*?\b(?:data|etl|database|warehouse|bi)\b', t):
        return True, "Software Test Engineer in Data"

    # 6. Core SDET / Software Development Engineer in Test (open to data & platform)
    if re.search(r'\b(sdet|software\s*development\s*engineer\s*in\s*test|qa\s*automation\s*engineer|automation\s*test\s*engineer|software\s*engineer\s*in\s*test)\b', t):
        return True, "SDET in Data"

    # 7. General Software Test / QA Engineer
    if re.search(r'\b(software\s*test\s*engineer|qa\s*engineer|quality\s*assurance\s*engineer|test\s*engineer)\b', t):
        return True, "Software Test Engineer in Data"

    return False, ""

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

    # 1. Location Eligibility Filter (India or Worldwide Remote)
    location_ok = is_remote_india_or_worldwide(location)
    if not location_ok:
        return {"eligible": False, "match_score": 0, "location_ok": False}

    # 2. STRICT TITLE FILTER: The title itself MUST be in scope!
    in_scope, category = is_title_in_scope(title)
    if not in_scope:
        return {"eligible": False, "match_score": 0, "location_ok": location_ok}

    # Base score strictly for in-scope title
    title_score = 65

    # 3. Extract and Score Skills to calculate match percentage
    matched_skills = []
    skill_score = 0
    for skill, weight in PROFILE.get("must_have_skills", {}).items():
        if re.search(r'\b' + re.escape(skill) + r'\b', full_text):
            skill_score += weight
            matched_skills.append(skill)

    total_score = title_score + min(skill_score, 35)

    eligible = (total_score >= MIN_SCORE_THRESHOLD) and location_ok

    return {
        "eligible": eligible,
        "match_score": min(total_score, 100),
        "category": category,
        "matched_skills": sorted(list(set(matched_skills))),
        "location_ok": location_ok
    }
