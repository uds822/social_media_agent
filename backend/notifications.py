import httpx
import logging
import asyncio
from config import settings

logger = logging.getLogger(__name__)


async def send_telegram_notification_async(message: str):
    """Sends a message to the configured Telegram chat (async version)."""
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id

    if not token or not chat_id:
        logger.warning("Telegram credentials not configured. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Telegram notification sent successfully.")
            return True
    except Exception as e:
        logger.error("Failed to send Telegram notification: %s", e)
        return False


def send_telegram_notification(message: str):
    """Synchronous wrapper for send_telegram_notification_async."""
    try:
        # Try to get the running event loop
        loop = asyncio.get_running_loop()
        # If we're in an async context, create a task
        asyncio.create_task(send_telegram_notification_async(message))
        return True
    except RuntimeError:
        # No event loop running, create a new one
        return asyncio.run(send_telegram_notification_async(message))
