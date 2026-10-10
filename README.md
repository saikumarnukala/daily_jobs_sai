# 🎯 Remote Job Scraper & Daily Alert Bot

An automated job search pipeline tailored for **Saikumar Nukala** (`ETL / Data Quality Test Engineer`), powered by resources from [awesome-remote-job](https://github.com/lukasz-madon/awesome-remote-job).

---

## 🚀 Features

* **Multi-Source Ingestion:** Automatically crawls remote job feeds (RemoteOK, Remotive, Jobicy, WeWorkRemotely RSS) and direct Greenhouse ATS endpoints for remote-first companies (GitLab, Elastic, etc.).
* **Intelligent Resume Matching:** Evaluates roles against your 5+ years of experience across **ETL/DWH Testing**, **Data Quality (Informatica DQ, DQE)**, **Advanced SQL**, **Python Automation**, **Postman API**, and **Snowflake/AWS**.
* **Zero Duplicates:** SQLite database (`jobs.db`) tracks every posting so you only receive alerts for brand-new jobs.
* **Instant Alerts:** Optional push alerts to **Telegram** or **Discord**.
* **Interactive HTML Dashboard:** Generates a glassmorphic dashboard (`job_digest.html`) with direct one-click apply links.

---

## 🛠️ How to Run

### 1. One-Off Scrape & Alert
```powershell
python job_monitor.py
```

### 2. View Database Tracking Statistics
```powershell
python job_monitor.py --stats
```

### 3. Regenerate the HTML Dashboard
```powershell
python job_monitor.py --digest
```

### 4. Continuous Background Daemon (e.g. Every 6 Hours)
```powershell
python job_monitor.py --daemon --interval 360
```

---

## 📱 Setting Up Push & Email Alerts

### 📧 Email Alerts (saikumar.kumar.qa@gmail.com):
1. Go to your Google Account > **Security** > **2-Step Verification** > **App passwords**.
2. Create an App password named `JobMonitor`.
3. You can either:
   * Add it to `config.py`:
     ```python
     NOTIFICATIONS = {
         "email_recipient": "saikumar.kumar.qa@gmail.com",
         "smtp_sender": "your_email@gmail.com",
         "smtp_password": "xxxx xxxx xxxx xxxx",  # 16-character app password
     }
     ```
   * Or set environment variables:
     `GMAIL_USER=your_email@gmail.com` and `GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx`

---

## 🤖 Automated Daily Execution with GitHub Actions

This repository includes a scheduled GitHub Actions workflow [`.github/workflows/daily_job_monitor.yml`](.github/workflows/daily_job_monitor.yml) that automatically runs every morning at **08:30 AM IST (03:00 UTC)**:

1. In your GitHub repository (`daily_jobs_sai`), go to **Settings** > **Secrets and variables** > **Actions**.
2. Add the following repository secrets:
   * `GMAIL_USER`: Your Gmail address
   * `GMAIL_APP_PASSWORD`: Your 16-character Google App Password
   * `DISCORD_WEBHOOK_URL` (optional)
   * `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` (optional)
3. Every morning, GitHub Actions will:
   * Crawl remote boards and ATS endpoints
   * Score against your resume
   * Send an HTML email alert with fresh matches directly to `saikumar.kumar.qa@gmail.com`
   * Commit the updated `jobs.db` and `job_digest.html` automatically.

---

### Discord Webhook:
1. Open Discord > Server Settings > Integrations > Create Webhook.
2. Paste the URL into `config.py`.

### Telegram Bot:
1. Chat with `@BotFather` on Telegram to create a bot and get your token.
2. Get your Chat ID from `@userinfobot`.
3. Paste both into `config.py`.

---

## ⏰ Scheduling on Windows

To run this automatically every morning at 9:00 AM via Windows Task Scheduler:

1. Open PowerShell as Administrator.
2. Run:
   ```powershell
   $action = New-ScheduledTaskAction -Execute "python.exe" -Argument "d:\Scripts\test\job_monitor.py" -WorkingDirectory "d:\Scripts\test"
   $trigger = New-ScheduledTaskTrigger -Daily -At 9am
   Register-ScheduledTask -TaskName "DailyJobMonitor" -Action $action -Trigger $trigger
   ```
