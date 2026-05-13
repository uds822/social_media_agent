"""
meta_publisher.py — Publish posts to Facebook Page and Instagram Business Account
using the Meta Graph API.

Required Meta App Permissions:
  - pages_manage_posts
  - pages_read_engagement
  - instagram_basic
  - instagram_content_publish
"""
from __future__ import annotations

import base64
import logging
from typing import Dict, Any, Optional, Tuple

import httpx

from config import settings
from image_generator import upload_image_bytes_to_cloudinary

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v19.0"


def _ensure_publishable_image_url(image_url: str) -> Optional[str]:
    """
    Meta requires a public HTTPS image URL.
    If we only have an inline data URL preview, upload it to Cloudinary now.
    """
    if not image_url:
        return None
    if image_url.startswith("http://") or image_url.startswith("https://"):
        return image_url
    if not image_url.startswith("data:image/"):
        logger.warning("Unsupported image URL format for publishing.")
        return None

    try:
        _, encoded = image_url.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        return upload_image_bytes_to_cloudinary(image_bytes)
    except Exception as e:
        logger.error("Failed to convert inline preview image into a hosted URL: %s", e)
        return None


def _graph_get(path: str, params: Dict) -> Dict:
    url = f"{GRAPH_BASE}/{path}"
    params["access_token"] = settings.facebook_page_access_token
    response = httpx.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _graph_post(path: str, data: Dict) -> Dict:
    url = f"{GRAPH_BASE}/{path}"
    data["access_token"] = settings.facebook_page_access_token
    response = httpx.post(url, data=data, timeout=60)
    response.raise_for_status()
    return response.json()


# ── Facebook Page ─────────────────────────────────────────────────────────────

def publish_to_facebook(caption: str, hashtags: str, image_url: str) -> Optional[str]:
    """
    Post an image to the Facebook Page.
    Returns the post ID on success, or None on failure.
    """
    if not settings.facebook_page_id or not settings.facebook_page_access_token:
        logger.warning("Facebook credentials not configured — skipping FB publish")
        return None

    full_message = f"{caption}\n\n{hashtags}"

    try:
        # Upload photo with message
        result = _graph_post(
            f"{settings.facebook_page_id}/photos",
            {
                "url":     image_url,
                "message": full_message,
            },
        )
        post_id = result.get("id") or result.get("post_id")
        logger.info("Published to Facebook: post_id=%s", post_id)
        return post_id
    except Exception as e:
        logger.error("Facebook publish failed: %s", e)
        return None


# ── Instagram ─────────────────────────────────────────────────────────────────

def publish_to_instagram(caption: str, hashtags: str, image_url: str) -> Optional[str]:
    """
    Publish an image to Instagram Business Account (2-step: create container → publish).
    Returns the Instagram media ID on success, or None on failure.
    """
    if not settings.instagram_business_account_id or not settings.facebook_page_access_token:
        logger.warning("Instagram credentials not configured — skipping IG publish")
        return None

    full_caption = f"{caption}\n\n{hashtags}"
    ig_id = settings.instagram_business_account_id

    try:
        # Step 1: Create media container
        container_result = _graph_post(
            f"{ig_id}/media",
            {
                "image_url": image_url,
                "caption":   full_caption,
            },
        )
        container_id = container_result.get("id")
        if not container_id:
            raise ValueError(f"No container ID returned: {container_result}")

        # Step 2: Publish the container
        publish_result = _graph_post(
            f"{ig_id}/media_publish",
            {"creation_id": container_id},
        )
        media_id = publish_result.get("id")
        logger.info("Published to Instagram: media_id=%s", media_id)
        return media_id
    except Exception as e:
        logger.error("Instagram publish failed: %s", e)
        return None


# ── Combined publisher ────────────────────────────────────────────────────────

def publish_post(post_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Publish to both Facebook and Instagram.
    Returns (facebook_post_id, instagram_post_id, error_message, resolved_image_url).
    """
    image_url = post_data.get("image_url", "")
    caption   = post_data.get("caption", "")
    hashtags  = post_data.get("hashtags", "")

    if not image_url:
        return None, None, "No image URL available for publishing.", None

    publishable_image_url = _ensure_publishable_image_url(image_url)
    if not publishable_image_url:
        return None, None, "Image preview exists, but a public hosted URL could not be prepared for publishing.", None

    fb_id = publish_to_facebook(caption, hashtags, publishable_image_url)
    ig_id = publish_to_instagram(caption, hashtags, publishable_image_url)

    error = None
    if not fb_id and not ig_id:
        error = "Failed to publish to both Facebook and Instagram."
    elif not fb_id:
        error = "Published to Instagram only. Facebook publish failed."
    elif not ig_id:
        error = "Published to Facebook only. Instagram publish failed."

    return fb_id, ig_id, error, publishable_image_url
