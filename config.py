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
MIN_SCORE_THRESHOLD = 50

# Candidate Profile & Target Roles
PROFILE = {
    "name": "Saikumar Nukala",
    "target_roles": [
        "ETL Test Engineer",
        "Data Quality Engineer",
        "SDET in Data",
        "Software Test Engineer in Data",
        "ETL Database Testing"
    ],
    # High-Priority In-Scope Title Patterns
    "in_scope_title_patterns": [
        # 1. ETL Test Engineer / ETL QA
        r'\b(etl\s*(?:test|testing|qa|tester|validation|engineer))\b',
        # 2. Data Quality Engineer / Data Quality QA / Analyst
        r'\b(data\s*quality\s*(?:engineer|analyst|qa|tester|specialist|lead))\b',
        # 3. SDET in Data
        r'\b(sdet\b.*?\b(?:data|pipeline|warehouse|platform|analytics|etl|sql|database))\b',
        r'\b(?:data|pipeline|warehouse|platform)\b.*?\bsdet\b',
        # 4. Software Test Engineer in Data / Data QA Engineer
        r'\b(data\s*(?:qa|test|testing|validation)(?:\s*automation)?\s*(?:engineer|analyst|lead|specialist))\b',
        r'\b(?:software\s*test|qa)\s*(?:engineer|analyst|lead|specialist)\b.*?\b(?:data|etl|database|warehouse|bi)\b',
        # 5. ETL Database Testing / Database Test Engineer / SQL QA
        r'\b(database\s*(?:test|testing|qa|tester|validation)\s*engineer)\b',
        r'\b(sql\s*(?:test|testing|qa|tester)\s*engineer)\b',
        r'\b(etl\s*(?:&|and)?\s*database\s*(?:test|testing|qa))\b'
    ],
    # Secondary Titles (Requires Data Testing Scope in Job Description)
    "secondary_title_patterns": [
        r'\b(sdet|qa\s*automation\s*engineer|test\s*automation\s*engineer|software\s*test\s*engineer|qa\s*engineer|quality\s*engineer|test\s*engineer)\b',
        r'\b(data\s*engineer|data\s*analyst|analytics\s*engineer|bi\s*engineer)\b'
    ],
    # Must-have core skills
    "must_have_skills": {
        "etl": 20,
        "data quality": 20,
        "data validation": 18,
        "database testing": 18,
        "source to target": 15,
        "data warehouse": 12,
        "dwh": 12,
        "sql": 15,
        "database": 8,
        "python": 12,
        "test automation": 10,
        "sdet": 12,
        "informatica": 10,
        "snowflake": 10,
        "aws": 7,
        "api testing": 8,
        "postman": 8,
        "selenium": 6,
        "cucumber": 6,
        "migration": 8,
        "reconciliation": 10,
        "power bi": 6,
        "spotfire": 6,
        "jenkins": 6,
        "jira": 4
    },
    # Location Filter: Must be workable remotely from India (India remote or Worldwide/Anywhere remote)
    # No timing/shift issues.
    "location_rules": {
        "india_indicators": [
            "india", "bengaluru", "bangalore", "hyderabad", "pune", 
            "chennai", "mumbai", "delhi", "noida", "gurgaon"
        ],
        "worldwide_indicators": [
            "worldwide", "anywhere", "work from anywhere", "global", 
            "everywhere", "remote - worldwide", "remote (worldwide)", "open remote"
        ],
        "foreign_restricted": [
            "usa", "united states", "us only", "only us", "u.s.", "canada", 
            "europe", "eu only", "uk only", "united kingdom", "germany", "france", 
            "spain", "italy", "netherlands", "slovakia", "poland", "latam", 
            "latin america", "brazil", "australia", "japan", "california", 
            "new york", "texas", "los angeles", "dallas", "toronto", "london",
            "berlin", "paris", "lisboa", "portugal", "austria", "wien", "mexico",
            "ireland", "dublin", "singapore", "kuala lumpur", "malaysia", "msida"
        ]
    }
}

# Remote-First Company Greenhouse Boards (from awesome-remote-job)
GREENHOUSE_BOARDS = [
    {"company": "Fivetran", "slug": "fivetran"},
    {"company": "Okta", "slug": "okta"},
    {"company": "GitLab", "slug": "gitlab"},
    {"company": "Elastic", "slug": "elastic"},
    {"company": "Cockroach Labs", "slug": "cockroachlabs"},
    {"company": "dbt Labs", "slug": "dbtlabs"},
    {"company": "Starburst", "slug": "starburst"},
    {"company": "MongoDB", "slug": "mongodb"},
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
