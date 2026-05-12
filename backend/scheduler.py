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
    """Auto-generate today's post at 4 AM so it's ready for 7 AM notification."""
    logger.info("⏰ Scheduler: auto-generating today's post …")
    try:
        from content_generator import generate_daily_post, fact_check, WEEKLY_SCHEDULE
        from image_generator import generate_and_upload_image
        from concurrent.futures import ThreadPoolExecutor
        from datetime import datetime, timezone
        import database as db

        # Clear any old pending posts so the new one has a clean queue
        db.expire_all_pending_posts()

        # Check if today is a festival
        today = datetime.now(timezone.utc)
        today_mm_dd = today.strftime("%m-%d")
        
        if today_mm_dd in FESTIVALS:
            festival_name = FESTIVALS[today_mm_dd]
            logger.info("🎉 Today is %s! Auto-generating festival post.", festival_name)
            post_data = generate_daily_post(post_type="festival_greeting", subject=festival_name, language="hindi")
        else:
            post_data = generate_daily_post(for_tomorrow=False)

        # Run fact-check + image generation in PARALLEL
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_fc  = executor.submit(fact_check, post_data)
            future_img = executor.submit(generate_and_upload_image, post_data)
            post_data["fact_check_status"] = future_fc.result(timeout=30)
            image_url = future_img.result(timeout=60)

        if image_url:
            post_data["image_url"] = image_url

        db.create_post(post_data)
        logger.info("✅ Today's post auto-generated and stored. Waiting for 7 AM notification.")
        
    except Exception as e:
        logger.exception("❌ Auto-generation failed: %s", e)
        # Notify admin about the failure too
        try:
            from notifications import send_telegram_notification
            send_telegram_notification(f"⚠️ *Auto-generation failed*\nError: {str(e)[:200]}\nPlease generate manually from the dashboard.")
        except:
            pass

def _job_send_morning_notification():
    """Send the 7 AM Telegram notification if a post is ready."""
    logger.info("⏰ Scheduler: sending 7 AM morning notification …")
    try:
        import database as db
        from notifications import send_telegram_notification
        
        post = db.get_pending_post()
        if post:
            post_type = post.get("post_type", "new")
            post_label = post_type.replace('_', ' ').title()
            msg = (
                f"📋 *Buniyaad — Post Ready for Review*\n\n"
                f"Today's *{post_label}* post has been auto-generated!\n\n"
                f"🔗 Open the dashboard to review, edit, and approve it.\n"
                f"Fact Check: {post.get('fact_check_status', 'N/A')}"
            )
            send_telegram_notification(msg)
        else:
            logger.warning("No pending post found for 7 AM notification.")
    except Exception as e:
        logger.exception("❌ Morning notification failed: %s", e)





def _job_cleanup_expired():
    """Delete posts older than 7 days, including unprocessed generated/rejected ones."""
    logger.info("⏰ Scheduler: cleaning up expired posts …")
    try:
        import database as db
        # Delete posts with an explicit expires_at timestamp that has passed
        count = db.delete_expired_posts()
        # Also delete old generated/rejected/expired posts older than 7 days by created_at
        count += db.delete_old_stale_posts(days=7)
        logger.info("Cleanup done. Total deleted: %d", count)
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

    # Auto-generate today's post at 4:00 AM IST
    _scheduler.add_job(
        _job_generate_daily_post,
        CronTrigger(
            hour=settings.daily_post_hour,
            minute=settings.daily_post_minute,
            timezone="Asia/Kolkata",
        ),
        id="daily_post",
        name="Auto-Generate Post (4 AM)",
        replace_existing=True,
    )

    # Send notification at 7:00 AM IST
    _scheduler.add_job(
        _job_send_morning_notification,
        CronTrigger(
            hour=settings.notification_hour,
            minute=settings.notification_minute,
            timezone="Asia/Kolkata",
        ),
        id="morning_notification",
        name="Morning Notification (7 AM)",
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
