"""
Configuration settings for the Automated Job Scraper & Alert System.
Tuned for Saikumar Nukala - ETL / Data Quality Test Engineer.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "jobs.db"
DIGEST_HTML_PATH = BASE_DIR / "job_digest.html"
RESUME_PDF_PATH = BASE_DIR / "Saikumar_Nukala_ETL_Data_Quality_Test_Engineer.pdf"

# Load local .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Minimum score to trigger an alert (out of 100)
MIN_SCORE_THRESHOLD = 45

# Candidate Profile Keywords (Weighted for Scoring)
PROFILE = {
    "name": "Saikumar Nukala",
    "target_titles": [
        "etl", "data quality", "data test", "data qa", "dwh test", 
        "qa automation", "sdet", "test engineer", "quality engineer", 
        "data validation", "software test engineer", "bi test"
    ],
    "must_have_skills": {
        "etl": 15,
        "data quality": 15,
        "sql": 12,
        "python": 12,
        "data validation": 12,
        "data warehouse": 10,
        "dwh": 10,
        "test automation": 10,
        "api testing": 8,
        "postman": 8,
        "selenium": 8,
        "cucumber": 8,
        "snowflake": 8,
        "aws": 7,
        "informatica": 10,
        "jenkins": 6,
        "power bi": 7,
        "spotfire": 6,
        "jira": 4,
        "regression": 6,
        "database": 5
    },
    # Locations acceptable (Saikumar is in India, available for IST, UK/EU mornings, US East evenings)
    "location_preferences": {
        "preferred": ["india", "remote", "worldwide", "anywhere", "apac", "emea", "global"],
        "restricted": ["us only", "usa only", "only us", "must reside in the us", "canada only", "germany only", "uk only"]
    }
}

# Remote-First Company Greenhouse Boards (from awesome-remote-job)
GREENHOUSE_BOARDS = [
    {"company": "GitLab", "slug": "gitlab"},
    {"company": "Elastic", "slug": "elastic"},
]

# Remote Job Board APIs
API_SOURCES = {
    "remotive": True,
    "remoteok": True,
    "jobicy": True,
    "weworkremotely": True,
    "greenhouse": True
}

# Alert Notifications
# Leave empty or fill in to enable instant push notifications
NOTIFICATIONS = {
    # Email Alert Settings
    "email_recipient": os.environ.get("EMAIL_RECIPIENT", "saikumar.kumar.qa@gmail.com"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_sender": os.environ.get("GMAIL_USER", "saikumar.nukala.qa@gmail.com"),
    "smtp_password": os.environ.get("GMAIL_APP_PASSWORD", ""),

    # Discord Webhook URL (optional)
    "discord_webhook_url": os.environ.get("DISCORD_WEBHOOK_URL", ""),

    # Telegram Bot Token & Chat ID (optional)
    "telegram_bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),

    # Generate HTML digest file on every run
    "generate_html_digest": True,
}
