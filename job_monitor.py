"""
Main orchestrator for the Automated Job Scraper & Daily Alert Bot.
Usage:
    python job_monitor.py           # Run full scrape, score, save, alert & generate HTML
    python job_monitor.py --digest  # Regenerate HTML dashboard from existing DB
    python job_monitor.py --stats   # View job tracking database statistics
"""
import sys
import time
import argparse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from db import init_db, save_job, get_new_jobs, mark_jobs_alerted, get_job_stats, get_connection
from scraper import scrape_and_match_all
from notifier import generate_html_digest, send_telegram_alert, send_discord_alert, send_email_alert
from config import NOTIFICATIONS, DIGEST_HTML_PATH, PROFILE

def run_job_monitor():
    print(f"\n{'='*65}")
    print(f"🎯 REMOTE JOB MONITOR: {PROFILE['name']}")
    print(f"   Target: ETL / Data Quality / QA Automation / SQL & Python")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}\n")

    # 1. Initialize SQLite Database
    init_db()

    # 2. Scrape & Score Jobs
    print("📡 Ingesting from remote boards & remote-first ATS endpoints...")
    matched_jobs = scrape_and_match_all()
    print(f"   ✓ Discovered {len(matched_jobs)} qualified matches exceeding score threshold.")

    # 3. Save into DB (Zero duplicate guarantee)
    new_count = 0
    newly_saved_jobs = []
    for job in matched_jobs:
        if save_job(job):
            new_count += 1
            newly_saved_jobs.append(job)

    print(f"   ✓ Added {new_count} brand-new jobs to database (previous duplicates skipped).")

    # 4. Fetch NEW jobs to alert
    jobs_to_alert = get_new_jobs()

    # 5. Send Notifications
    if jobs_to_alert:
        print(f"\n📢 Sending alerts for {len(jobs_to_alert)} new jobs...")

        # Email Notification
        recipient = NOTIFICATIONS.get("email_recipient")
        if recipient:
            if send_email_alert(jobs_to_alert, recipient):
                print(f"   ✓ Email notification delivered to {recipient}.")
            else:
                print(f"   ℹ️  Email alert configured for {recipient} (add Gmail App Password to config.py or GMAIL_APP_PASSWORD env var).")

        if NOTIFICATIONS.get("telegram_bot_token"):
            if send_telegram_alert(jobs_to_alert):
                print("   ✓ Telegram notification delivered successfully.")
            else:
                print("   ✗ Telegram notification failed or not configured.")

        if NOTIFICATIONS.get("discord_webhook_url"):
            if send_discord_alert(jobs_to_alert):
                print("   ✓ Discord webhook delivered successfully.")
            else:
                print("   ✗ Discord notification failed or not configured.")

        # Mark jobs as alerted so they don't notify again
        alerted_urls = [j["url"] for j in jobs_to_alert]
        mark_jobs_alerted(alerted_urls)
    else:
        print("\nℹ️  No new unalerted jobs on this run.")

    # 6. Generate HTML Digest Dashboard
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM jobs ORDER BY match_score DESC")
        all_jobs_rows = [dict(r) for r in cursor.fetchall()]
        for j in all_jobs_rows:
            import json
            j["matched_skills"] = json.loads(j["matched_skills"]) if j.get("matched_skills") else []
    
    digest_path = generate_html_digest(all_jobs_rows)
    digest_url = str(digest_path).replace("\\", "/")
    print(f"\n📊 Interactive HTML Dashboard generated at:")
    print(f"   file:///{digest_url}")

    # 7. Print Terminal Summary
    print(f"\n{'='*65}")
    print(f"Top Active Matches:")
    for idx, j in enumerate(all_jobs_rows[:8], 1):
        skills_summary = ", ".join(j.get("matched_skills", [])[:5])
        print(f"{idx}. [{j['match_score']}% Match] {j['title']} @ {j['company']}")
        print(f"   📍 {j.get('location', 'Remote')} | 🏷️  {j.get('category')}")
        print(f"   ⚡ Skills: {skills_summary}")
        print(f"   🔗 {j['url']}")
        print()
    print(f"{'='*65}\n")

def show_stats():
    init_db()
    stats = get_job_stats()
    print("\n📊 Job Database Statistics:")
    total = sum(stats.values())
    print(f"   Total tracked: {total}")
    for status, count in stats.items():
        print(f"   - {status}: {count}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Automated Job Scraper & Alert System")
    parser.add_argument("--digest", action="store_true", help="Regenerate HTML digest from database")
    parser.add_argument("--stats", action="store_true", help="Show database stats")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background")
    parser.add_argument("--interval", type=int, default=360, help="Interval in minutes for daemon mode (default: 360)")
    args = parser.parse_args()

    if args.stats:
        show_stats()
    elif args.digest:
        init_db()
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM jobs ORDER BY match_score DESC")
            all_jobs_rows = [dict(r) for r in cursor.fetchall()]
            import json
            for j in all_jobs_rows:
                j["matched_skills"] = json.loads(j["matched_skills"]) if j.get("matched_skills") else []
        digest_path = generate_html_digest(all_jobs_rows)
        digest_url = str(digest_path).replace("\\", "/")
        print(f"HTML Digest regenerated: file:///{digest_url}")
    elif args.daemon:
        print(f"🔄 Starting Job Monitor Daemon (Every {args.interval} minutes)...")
        while True:
            run_job_monitor()
            print(f"Sleeping for {args.interval} minutes...")
            time.sleep(args.interval * 60)
    else:
        run_job_monitor()

if __name__ == "__main__":
    main()
