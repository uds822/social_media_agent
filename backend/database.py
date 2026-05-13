"""
database.py — Supabase client singleton + table helpers.

Table: posts
  id                 uuid  (default gen_random_uuid())
  post_type          text
  subject            text
  class_level        text
  topic              text
  image_url          text
  caption            text
  hashtags           text
  suggestions        text
  fact_check_status  text  ('verified' | 'unverified' | 'failed')
  status             text  ('generated' | 'awaiting_approval' | 'approved'
                            | 'published' | 'rejected' | 'failed' | 'expired')
  created_at         timestamptz  default now()
  approved_at        timestamptz
  published_at       timestamptz
  instagram_post_id  text
  facebook_post_id   text
  error_message      text
  expires_at         timestamptz
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise RuntimeError(
                "Supabase credentials not configured. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file."
            )
        _client = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _client


def _reset_client():
    """Force-reset the Supabase client on connection errors so the next call gets a fresh socket."""
    global _client
    _client = None


def _supabase_call(fn, retries: int = 2, delay: float = 1.0):
    """Execute a Supabase callable with automatic retry on transient network errors."""
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as e:
            last_err = e
            logger.warning("Supabase connection error (attempt %d/%d): %s", attempt + 1, retries, e)
            _reset_client()  # force fresh client/socket on next attempt
            if attempt < retries - 1:
                time.sleep(delay)
        except Exception as e:
            raise  # non-network errors bubble up immediately
    raise last_err


# ── CRUD helpers ─────────────────────────────────────────────────────────────

def create_post(data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new post row and return the created record."""
    allowed_keys = {
        "post_type", "subject", "class_level", "topic", "image_url",
        "caption", "hashtags", "suggestions", "fact_check_status", "status"
    }
    db_data = {k: v for k, v in data.items() if k in allowed_keys}
    return _supabase_call(lambda: get_client().table("posts").insert(db_data).execute().data[0])


def get_pending_post() -> Optional[Dict[str, Any]]:
    """Return the most recent post in awaiting_approval state."""
    def _query():
        result = (
            get_client().table("posts")
            .select("*")
            .eq("status", "awaiting_approval")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    return _supabase_call(_query)


def get_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    result = client.table("posts").select("*").eq("id", post_id).execute()
    return result.data[0] if result.data else None


def expire_all_pending_posts() -> int:
    """Mark all currently awaiting_approval posts as expired to clear the dashboard queue."""
    client = get_client()
    result = client.table("posts").update({"status": "expired"}).eq("status", "awaiting_approval").execute()
    count = len(result.data) if result.data else 0
    if count > 0:
        logger.info("Archived %d old pending posts", count)
    return count


def update_post(post_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    result = client.table("posts").update(updates).eq("id", post_id).execute()
    return result.data[0]


def get_recent_posts(days: int = 7) -> List[Dict[str, Any]]:
    """Return published posts from the last `days` days."""
    client = get_client()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    result = (
        client.table("posts")
        .select("*")
        .gte("created_at", since)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def delete_expired_posts() -> int:
    """Hard-delete posts whose expires_at < now(). Returns count deleted."""
    client = get_client()
    now = datetime.now(timezone.utc).isoformat()
    result = client.table("posts").delete().lt("expires_at", now).execute()
    count = len(result.data) if result.data else 0
    logger.info("Deleted %d expired posts", count)
    return count


def delete_old_stale_posts(days: int = 7) -> int:
    """Hard-delete generated/rejected/expired posts older than `days` days.
    These never get expires_at set so delete_expired_posts() misses them."""
    client = get_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    stale_statuses = ["generated", "rejected", "expired", "failed"]
    total = 0
    for status in stale_statuses:
        result = (
            client.table("posts")
            .delete()
            .eq("status", status)
            .lt("created_at", cutoff)
            .execute()
        )
        total += len(result.data) if result.data else 0
    if total > 0:
        logger.info("Deleted %d stale posts (generated/rejected/expired/failed)", total)
    return total



def clear_all_posts() -> int:
    """Hard-delete all posts in the database. Returns count deleted."""
    client = get_client()
    # PostgREST requires a filter to bulk delete. We use a condition that is always true.
    result = client.table("posts").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    count = len(result.data) if result.data else 0
    logger.warning("Database cleared: Deleted %d posts", count)
    return count


def get_user(username: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    result = client.table("users").select("*").eq("username", username).execute()
    return result.data[0] if result.data else None


def create_user(username: str, password_hash: str) -> Dict[str, Any]:
    client = get_client()
    result = client.table("users").insert({"username": username, "password_hash": password_hash}).execute()
    return result.data[0]


def update_user(username: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    result = client.table("users").update(updates).eq("username", username).execute()
    return result.data[0]


# ── SQL migration helper (run once) ──────────────────────────────────────────

MIGRATION_SQL = """
create extension if not exists "pgcrypto";

create table if not exists users (
  username       text primary key,
  password_hash  text not null,
  backup_codes   text,
  created_at     timestamptz not null default now()
);

create table if not exists posts (
  id                 uuid         primary key default gen_random_uuid(),
  post_type          text         not null,
  subject            text,
  class_level        text,
  topic              text,
  image_url          text,
  caption            text,
  hashtags           text,
  suggestions        text,
  fact_check_status  text         default 'unverified',
  status             text         not null default 'generated',
  created_at         timestamptz  not null default now(),
  approved_at        timestamptz,
  published_at       timestamptz,
  instagram_post_id  text,
  facebook_post_id   text,
  error_message      text,
  expires_at         timestamptz
);

create index if not exists idx_posts_status     on posts(status);
create index if not exists idx_posts_created_at on posts(created_at desc);
create index if not exists idx_posts_expires_at on posts(expires_at);
"""
