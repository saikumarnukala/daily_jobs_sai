"""
Database module for storing jobs, tracking alerts, and preventing duplicates.
"""
import sqlite3
import json
from datetime import datetime
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT NOT NULL UNIQUE,
                match_score INTEGER,
                category TEXT,
                matched_skills TEXT,
                date_posted TEXT,
                status TEXT DEFAULT 'NEW',  -- NEW, ALERTED, APPLIED, DISMISSED
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def is_job_seen(url: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM jobs WHERE url = ?", (url,))
        return cursor.fetchone() is not None

def save_job(job: dict) -> bool:
    """Save a job if not already present. Returns True if newly inserted."""
    if is_job_seen(job["url"]):
        return False

    with get_connection() as conn:
        skills_str = json.dumps(job.get("matched_skills", []))
        conn.execute("""
            INSERT OR IGNORE INTO jobs 
            (id, source, title, company, location, url, match_score, category, matched_skills, date_posted, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW')
        """, (
            job["id"],
            job["source"],
            job["title"],
            job["company"],
            job.get("location", "Remote"),
            job["url"],
            job.get("match_score", 0),
            job.get("category", "General QA"),
            skills_str,
            job.get("date_posted", ""),
        ))
        conn.commit()
    return True

def get_new_jobs():
    """Retrieve all jobs marked as NEW (not yet alerted)."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM jobs 
            WHERE status = 'NEW' 
            ORDER BY match_score DESC
        """)
        rows = cursor.fetchall()
        jobs = []
        for r in rows:
            d = dict(r)
            d["matched_skills"] = json.loads(d["matched_skills"]) if d["matched_skills"] else []
            jobs.append(d)
        return jobs

def mark_jobs_alerted(job_urls: list):
    """Mark a batch of jobs as ALERTED so we don't alert the user again."""
    if not job_urls:
        return
    with get_connection() as conn:
        conn.executemany(
            "UPDATE jobs SET status = 'ALERTED' WHERE url = ?",
            [(u,) for u in job_urls]
        )
        conn.commit()

def get_job_stats():
    """Return counts of total, new, alerted, applied jobs."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count 
            FROM jobs 
            GROUP BY status
        """)
        return {r["status"]: r["count"] for r in cursor.fetchall()}
