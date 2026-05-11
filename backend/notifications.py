import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

def send_telegram_notification(message: str):
    """Sends a message to the configured Telegram chat."""
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    
    if not token or not chat_id:
        logger.warning("Telegram credentials not configured. Skipping notification.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram notification sent successfully.")
        return True
    except Exception as e:
        logger.error("Failed to send Telegram notification: %s", e)
        return False

