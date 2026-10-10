"""
Multi-source scraper fetching from Remote boards and remote-first company ATS endpoints.
"""
import urllib.request
import json
import ssl
import re
import html
import xml.etree.ElementTree as ET
from config import API_SOURCES, GREENHOUSE_BOARDS
from matcher import evaluate_job

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    cleanr = re.compile(r'<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return html.unescape(cleantext).strip()

def safe_fetch_json(url: str, timeout: int = 15):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            return json.loads(data)
    except Exception as e:
        # print(f"Fetch notice for {url}: {e}")
        return None

def fetch_remotive() -> list:
    results = []
    queries = [
        "https://remotive.com/api/remote-jobs?category=qa",
        "https://remotive.com/api/remote-jobs?search=qa",
        "https://remotive.com/api/remote-jobs?search=data",
        "https://remotive.com/api/remote-jobs?search=sql"
    ]
    for url in queries:
        data = safe_fetch_json(url)
        if data and "jobs" in data:
            for j in data["jobs"]:
                results.append({
                    "id": f"remotive-{j.get('id')}",
                    "source": "Remotive",
                    "title": j.get("title", ""),
                    "company": j.get("company_name", ""),
                    "location": j.get("candidate_required_location", "Remote"),
                    "url": j.get("url", ""),
                    "description": clean_html(j.get("description", "")),
                    "tags": j.get("tags", []),
                    "date_posted": j.get("publication_date", "")
                })
    return results

def fetch_remoteok() -> list:
    results = []
    tags = ["", "data", "testing", "sql", "python"]
    for tag in tags:
        url = f"https://remoteok.com/api{'?tag=' + tag if tag else ''}"
        data = safe_fetch_json(url, timeout=20)
        if isinstance(data, list):
            for j in data:
                if isinstance(j, dict) and "position" in j:
                    results.append({
                        "id": f"remoteok-{j.get('id')}",
                        "source": "RemoteOK",
                        "title": j.get("position", ""),
                        "company": j.get("company", ""),
                        "location": j.get("location", "Remote"),
                        "url": j.get("url", ""),
                        "description": clean_html(j.get("description", "")),
                        "tags": j.get("tags", []),
                        "date_posted": j.get("date", "")
                    })
    return results

def fetch_jobicy() -> list:
    results = []
    for tag in ["", "dev", "data"]:
        url = f"https://jobicy.com/api/v2/remote-jobs?count=50{'&tag=' + tag if tag else ''}"
        data = safe_fetch_json(url)
        if data and "jobs" in data:
            for j in data["jobs"]:
                results.append({
                    "id": f"jobicy-{j.get('id')}",
                    "source": "Jobicy",
                    "title": j.get("jobTitle", ""),
                    "company": j.get("companyName", ""),
                    "location": j.get("jobGeo", "Remote"),
                    "url": j.get("url", ""),
                    "description": clean_html(j.get("jobDescription", "")),
                    "tags": j.get("jobIndustry", []),
                    "date_posted": j.get("pubDate", "")
                })
    return results

def fetch_weworkremotely() -> list:
    results = []
    feeds = [
        "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss"
    ]
    for url in feeds:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    desc_elem = item.find("description")
                    pub_elem = item.find("pubDate")
                    
                    full_title = title_elem.text if title_elem is not None else ""
                    parts = full_title.split(":", 1)
                    company = parts[0].strip() if len(parts) > 1 else "Unknown"
                    title = parts[1].strip() if len(parts) > 1 else full_title

                    link = link_elem.text if link_elem is not None else ""
                    desc = clean_html(desc_elem.text if desc_elem is not None else "")
                    pub = pub_elem.text if pub_elem is not None else ""

                    if link:
                        results.append({
                            "id": f"wwr-{hash(link)}",
                            "source": "WeWorkRemotely",
                            "title": title,
                            "company": company,
                            "location": "Remote",
                            "url": link,
                            "description": desc,
                            "tags": [],
                            "date_posted": pub
                        })
        except Exception:
            pass
    return results

def fetch_greenhouse_boards() -> list:
    results = []
    for board in GREENHOUSE_BOARDS:
        company_name = board["company"]
        slug = board["slug"]
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        data = safe_fetch_json(url)
        if data and "jobs" in data:
            for j in data["jobs"]:
                loc_obj = j.get("location") or {}
                location = loc_obj.get("name", "Remote") if isinstance(loc_obj, dict) else str(loc_obj)
                results.append({
                    "id": f"greenhouse-{slug}-{j.get('id')}",
                    "source": f"{company_name} (Direct ATS)",
                    "title": j.get("title", ""),
                    "company": company_name,
                    "location": location,
                    "url": j.get("absolute_url", ""),
                    "description": "",  # Detailed description can be fetched if title matches
                    "tags": [],
                    "date_posted": j.get("updated_at", "")
                })
    return results

def scrape_and_match_all() -> list:
    """Scrapes all active sources, evaluates each job, and returns scored matching jobs."""
    raw_jobs = []

    if API_SOURCES.get("remotive"):
        raw_jobs.extend(fetch_remotive())
    if API_SOURCES.get("remoteok"):
        raw_jobs.extend(fetch_remoteok())
    if API_SOURCES.get("jobicy"):
        raw_jobs.extend(fetch_jobicy())
    if API_SOURCES.get("weworkremotely"):
        raw_jobs.extend(fetch_weworkremotely())
    if API_SOURCES.get("greenhouse"):
        raw_jobs.extend(fetch_greenhouse_boards())

    # Deduplicate by URL
    seen_urls = set()
    unique_raw = []
    for j in raw_jobs:
        u = j.get("url", "").strip()
        if u and u not in seen_urls:
            seen_urls.add(u)
            unique_raw.append(j)

    matched_jobs = []
    for j in unique_raw:
        evaluation = evaluate_job(
            title=j["title"],
            description=j["description"],
            location=j["location"],
            tags=j["tags"]
        )
        if evaluation["eligible"]:
            j["match_score"] = evaluation["match_score"]
            j["category"] = evaluation["category"]
            j["matched_skills"] = evaluation["matched_skills"]
            matched_jobs.append(j)

    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_jobs
