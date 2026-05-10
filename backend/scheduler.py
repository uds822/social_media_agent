"""
scheduler.py — APScheduler jobs for daily post generation and cleanup.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


FESTIVALS = {
    "01-01": "New Year",
    "01-14": "Makar Sankranti",
    "01-26": "Republic Day",
    "03-08": "Maha Shivaratri",
    "03-25": "Holi",
    "04-11": "Eid al-Fitr",
    "08-15": "Independence Day",
    "10-02": "Gandhi Jayanti",
    "10-12": "Dussehra",
    "10-31": "Diwali",
    "11-01": "Chhath Puja",
    "12-25": "Christmas",
}

def _job_generate_daily_post():
    """Generate and store today's post in the DB. Auto-handles festivals."""
    logger.info("⏰ Scheduler: generating daily post …")
    try:
        from content_generator import generate_daily_post
        from image_generator import generate_and_upload_image
        import database as db
        from notifications import send_telegram_notification

        today_mm_dd = datetime.now(timezone.utc).strftime("%m-%d")
        
        if today_mm_dd in FESTIVALS:
            festival_name = FESTIVALS[today_mm_dd]
            logger.info("🎉 Today is %s! Auto-generating festival post.", festival_name)
            post_data = generate_daily_post(post_type="festival_greeting", subject=festival_name, language="hindi")
        else:
            post_data = generate_daily_post()

        image_url = generate_and_upload_image(post_data)
        if image_url:
            post_data["image_url"] = image_url

        db.create_post(post_data)
        logger.info("✅ Daily post created and stored.")
        
        # Send Telegram Notification
        post_type_label = post_data.get("post_type", "new")
        msg = f"🎉 *EduPlatform Dashboard*\nA {post_type_label.replace('_', ' ').title()} post has been automatically generated! Log in to the dashboard to approve and publish."
        send_telegram_notification(msg)
        
    except Exception as e:
        logger.exception("❌ Daily post generation failed: %s", e)


def _job_cleanup_expired():
    """Delete posts older than 7 days."""
    logger.info("⏰ Scheduler: cleaning up expired posts …")
    try:
        import database as db
        count = db.delete_expired_posts()
    except Exception as e:
        logger.exception("❌ Cleanup job failed: %s", e)

def _job_check_live_news():
    """Periodically checks DuckDuckGo for breaking exam updates."""
    logger.info("⏰ Scheduler: scanning for live breaking news …")
    try:
        from content_generator import check_and_generate_trending_news
        from image_generator import generate_and_upload_image
        import database as db
        from notifications import send_telegram_notification

        # Check a few major topics
        topics_to_check = ["CBSE Board", "JEE NEET", "Bihar Board"]
        for topic in topics_to_check:
            post_data = check_and_generate_trending_news(topic)
            if post_data:
                logger.info("🚨 Breaking news detected for %s! Generating post.", topic)
                image_url = generate_and_upload_image(post_data)
                if image_url:
                    post_data["image_url"] = image_url
                post_data["status"] = "awaiting_approval"
                db.create_post(post_data)
                
                # Notify admin immediately
                msg = f"🚨 *BREAKING NEWS DETECTED: {topic}*\nA new trending awareness post was just generated automatically from live news! Log in to review it."
                send_telegram_notification(msg)
                
                # Only process one breaking news per cycle to avoid spam
                break
                
    except Exception as e:
        logger.exception("❌ Live news check failed: %s", e)


def start_scheduler():
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

    # Daily post — e.g. 07:00 IST
    _scheduler.add_job(
        _job_generate_daily_post,
        CronTrigger(
            hour=settings.daily_post_hour,
            minute=settings.daily_post_minute,
            timezone="Asia/Kolkata",
        ),
        id="daily_post",
        name="Generate Daily Post",
        replace_existing=True,
    )

    # Daily cleanup — 02:00 IST
    _scheduler.add_job(
        _job_cleanup_expired,
        CronTrigger(hour=2, minute=0, timezone="Asia/Kolkata"),
        id="cleanup",
        name="Cleanup Expired Posts",
        replace_existing=True,
    )

    # Live News Scanner — Runs every 4 hours
    _scheduler.add_job(
        _job_check_live_news,
        CronTrigger(hour="9,13,17,21", minute=30, timezone="Asia/Kolkata"),
        id="live_news_scanner",
        name="Scan Live News",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started. Daily post at %02d:%02d IST.",
                settings.daily_post_hour, settings.daily_post_minute)


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
