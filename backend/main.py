"""
main.py — FastAPI application entry point for the Buniyaad Social Media Agent.

Endpoints:
  POST /auth/login          – get JWT token
  GET  /api/health          – health check
  POST /api/posts/generate  – manually trigger post generation
  GET  /api/posts/pending   – get the current awaiting_approval post
  GET  /api/posts/{id}      – get a specific post
  POST /api/posts/{id}/approve  – approve and publish
  POST /api/posts/{id}/reject   – reject a post
  POST /api/posts/{id}/regenerate – regenerate a post
  PATCH /api/posts/{id}/caption  – update caption/hashtags
  GET  /api/posts/history   – get last 7 days of posts
  GET  /api/status          – Meta API and LLM connection status
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
import hashlib
import secrets
import dotenv

import auth
import database as db
from config import settings
from scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── App lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Buniyaad Social Media Agent starting …")
    start_scheduler()
    yield
    logger.info("🛑 Shutting down …")
    stop_scheduler()


app = FastAPI(
    title="Buniyaad Social Media Agent API",
    description="AI-powered social media content generation and publishing system for Edu Platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*" # if we change allow_credentials to False
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int  # seconds


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    username: str
    backup_code: str
    new_password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class GenerateRequest(BaseModel):
    post_type:   Optional[str] = None   # null → use weekly schedule
    subject:     Optional[str] = None
    class_level: Optional[str] = None
    language:    str = "english"         # 'english' or 'hindi'


class UpdateCaptionRequest(BaseModel):
    caption:  Optional[str] = None
    hashtags: Optional[str] = None


class UpdateKeysRequest(BaseModel):
    # API Keys
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    # Model Names
    openrouter_model: Optional[str] = None
    groq_model: Optional[str] = None
    nvidia_model: Optional[str] = None
    huggingface_model: Optional[str] = None
    # Active provider preference (openrouter | groq | nvidia | huggingface)
    active_provider: Optional[str] = None


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/register", tags=["Auth"])
def register(req: RegisterRequest):
    try:
        user = db.get_user(req.username)
        if user or req.username == settings.admin_username:
            raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        # If the table doesn't exist yet, we catch the exception and instruct the user
        if "relation \"users\" does not exist" in str(e):
            raise HTTPException(status_code=500, detail="The 'users' table does not exist in Supabase yet. Please run the MIGRATION_SQL.")
        raise
        
    db.create_user(req.username, hash_code(req.password))
    return {"message": "Account created successfully. You can now log in."}


@app.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
def login(req: LoginRequest):
    try:
        user = db.get_user(req.username)
    except Exception:
        user = None

    if user:
        if user["password_hash"] != hash_code(req.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    else:
        if req.username != settings.admin_username or req.password != settings.admin_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
    token = auth.create_token(req.username)
    return LoginResponse(
        token=token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

@app.post("/auth/change-password", tags=["Auth"])
def change_password(req: ChangePasswordRequest, username: str = Depends(auth.get_current_admin)):
    try:
        user = db.get_user(username)
    except Exception:
        user = None

    if user:
        if user["password_hash"] != hash_code(req.old_password):
            raise HTTPException(status_code=400, detail="Incorrect old password")
        db.update_user(username, {"password_hash": hash_code(req.new_password)})
    else:
        if req.old_password != settings.admin_password:
            raise HTTPException(status_code=400, detail="Incorrect old password")
        settings.admin_password = req.new_password
        dotenv.set_key(".env", "ADMIN_PASSWORD", req.new_password)
        
    return {"message": "Password updated successfully."}

@app.post("/auth/generate-backup-codes", tags=["Auth"])
def generate_backup_codes(username: str = Depends(auth.get_current_admin)):
    codes = [secrets.token_hex(4) for _ in range(5)]
    hashed_codes = [hash_code(c) for c in codes]
    hashed_str = ",".join(hashed_codes)
    
    try:
        user = db.get_user(username)
    except Exception:
        user = None

    if user:
        db.update_user(username, {"backup_codes": hashed_str})
    else:
        settings.backup_codes = hashed_str
        dotenv.set_key(".env", "BACKUP_CODES", hashed_str)
    
    return {"codes": codes, "message": "Save these codes securely. They will only be shown once."}

@app.post("/auth/reset-password", tags=["Auth"])
def reset_password(req: ResetPasswordRequest):
    try:
        user = db.get_user(req.username)
    except Exception:
        user = None

    if user:
        if not user.get("backup_codes"):
            raise HTTPException(status_code=400, detail="No backup codes configured for this account")
            
        hashed_input = hash_code(req.backup_code)
        saved_hashes = user["backup_codes"].split(",")
        if hashed_input not in saved_hashes:
            raise HTTPException(status_code=400, detail="Invalid backup code")
            
        saved_hashes.remove(hashed_input)
        new_hashed_str = ",".join(saved_hashes)
        db.update_user(req.username, {
            "password_hash": hash_code(req.new_password),
            "backup_codes": new_hashed_str
        })
    else:
        if req.username != settings.admin_username:
            raise HTTPException(status_code=400, detail="Invalid username")
        if not settings.backup_codes:
            raise HTTPException(status_code=400, detail="No backup codes configured for this account")
            
        hashed_input = hash_code(req.backup_code)
        saved_hashes = settings.backup_codes.split(",")
        if hashed_input not in saved_hashes:
            raise HTTPException(status_code=400, detail="Invalid backup code")
            
        saved_hashes.remove(hashed_input)
        new_hashed_str = ",".join(saved_hashes)
        settings.backup_codes = new_hashed_str
        dotenv.set_key(".env", "BACKUP_CODES", new_hashed_str)
        settings.admin_password = req.new_password
        dotenv.set_key(".env", "ADMIN_PASSWORD", req.new_password)
    
    return {"message": "Password reset successfully. You can now log in."}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "service": "Buniyaad Social Media Agent", "version": "1.0.0"}


# ── Status ────────────────────────────────────────────────────────────────────

@app.get("/api/status", tags=["System"])
def api_status(_: str = Depends(auth.get_current_admin)):
    # Determine active generator display based on settings.active_provider
    provider_display = {
        "openrouter":   (f"OpenRouter ({settings.openrouter_model})",  "#a78bfa"),
        "groq":         (f"Groq ({settings.groq_model})",              "#34d399"),
        "nvidia":       (f"NVIDIA ({settings.nvidia_model})",          "#76d9f5"),
        "huggingface":  (f"HuggingFace ({settings.huggingface_model})", "#fbbf24"),
    }
    active_gen, active_color = provider_display.get(
        settings.active_provider.lower(),
        (f"NVIDIA ({settings.nvidia_model})", "#76d9f5")
    )

    return {
        "openrouter_configured": bool(settings.openrouter_api_key),
        "groq_configured":       bool(settings.groq_api_key),
        "nvidia_configured":     bool(settings.nvidia_api_key),
        "huggingface_configured": bool(settings.huggingface_api_key),
        "supabase_configured":   bool(settings.supabase_url and "XXXX" not in settings.supabase_url),
        "cloudinary_configured": bool(settings.cloudinary_cloud_name and settings.cloudinary_cloud_name != "your_cloud_name"),
        "meta_configured": bool(
            settings.facebook_page_id and
            settings.facebook_page_access_token and
            "EAAxxxxx" not in settings.facebook_page_access_token
        ),
        "scheduler_running": True,
        # Current active model names
        "openrouter_model":   settings.openrouter_model,
        "groq_model":         settings.groq_model,
        "nvidia_model":       settings.nvidia_model,
        "huggingface_model":  settings.huggingface_model,
        # Active provider preference
        "active_provider":    settings.active_provider,
        # Active providers for UI badges
        "active_generator_text": active_gen,
        "active_generator_color": active_color,
        "active_fact_checker": f"Groq ({settings.groq_model})" if settings.groq_api_key else "Disabled",
    }


# ── Settings ──────────────────────────────────────────────────────────────────

@app.post("/api/settings/keys", tags=["Settings"])
def update_api_keys(req: UpdateKeysRequest, _: str = Depends(auth.get_current_admin)):
    import dotenv
    env_path = ".env"
    updates = {}
    
    if req.openrouter_api_key is not None:
        settings.openrouter_api_key = req.openrouter_api_key
        dotenv.set_key(env_path, "OPENROUTER_API_KEY", req.openrouter_api_key)
        updates["openrouter"] = "updated"
        
    if req.groq_api_key is not None:
        settings.groq_api_key = req.groq_api_key
        dotenv.set_key(env_path, "GROQ_API_KEY", req.groq_api_key)
        updates["groq"] = "updated"
        
    if req.nvidia_api_key is not None:
        settings.nvidia_api_key = req.nvidia_api_key
        dotenv.set_key(env_path, "NVIDIA_API_KEY", req.nvidia_api_key)
        updates["nvidia"] = "updated"
        
    if req.huggingface_api_key is not None:
        settings.huggingface_api_key = req.huggingface_api_key
        dotenv.set_key(env_path, "HUGGINGFACE_API_KEY", req.huggingface_api_key)
        updates["huggingface_key"] = "updated"

    # Model name updates
    if req.openrouter_model is not None:
        settings.openrouter_model = req.openrouter_model
        dotenv.set_key(env_path, "OPENROUTER_MODEL", req.openrouter_model)
        updates["openrouter_model"] = "updated"

    if req.groq_model is not None:
        settings.groq_model = req.groq_model
        dotenv.set_key(env_path, "GROQ_MODEL", req.groq_model)
        updates["groq_model"] = "updated"

    if req.nvidia_model is not None:
        settings.nvidia_model = req.nvidia_model
        dotenv.set_key(env_path, "NVIDIA_MODEL", req.nvidia_model)
        updates["nvidia_model"] = "updated"

    if req.huggingface_model is not None:
        settings.huggingface_model = req.huggingface_model
        dotenv.set_key(env_path, "HUGGINGFACE_MODEL", req.huggingface_model)
        updates["huggingface_model"] = "updated"

    if req.active_provider is not None:
        valid_providers = ("openrouter", "groq", "nvidia", "huggingface")
        if req.active_provider.lower() not in valid_providers:
            raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {valid_providers}")
        settings.active_provider = req.active_provider.lower()
        dotenv.set_key(env_path, "ACTIVE_PROVIDER", req.active_provider.lower())
        updates["active_provider"] = req.active_provider
        
    if not updates:
        return {"message": "No keys provided to update."}
        
    return {"message": "API keys updated successfully.", "updates": updates}


# ── Post generation ───────────────────────────────────────────────────────────

def _run_generation(post_type, subject, class_level, language="english"):
    """Background task: generate post text, then fact-check + image in parallel."""
    try:
        from content_generator import generate_daily_post, fact_check
        from image_generator import generate_and_upload_image

        # Step 1: Generate post text (LLM call 1)
        post_data = generate_daily_post(post_type, subject, class_level, language)

        # Step 2: Fact-check + image generation in PARALLEL (saves ~15-30s)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_fc  = executor.submit(fact_check, post_data)
            future_img = executor.submit(generate_and_upload_image, post_data)
            fact_status = future_fc.result(timeout=30)
            image_url   = future_img.result(timeout=60)

        post_data["fact_check_status"] = fact_status
        if image_url:
            post_data["image_url"] = image_url

        db.create_post(post_data)
        logger.info("✅ Post generated: type=%s language=%s fact=%s", post_type, language, fact_status)
    except Exception as e:
        logger.exception("❌ Manual generation failed: %s", e)


@app.post("/api/posts/generate", tags=["Posts"], status_code=202)
def generate_post(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(auth.get_current_admin),
):
    # Instantly clear the queue so the frontend doesn't poll an old ghost post
    db.expire_all_pending_posts()
    
    background_tasks.add_task(_run_generation, req.post_type, req.subject, req.class_level, req.language)
    return {"message": "Post generation started in the background. Check /api/posts/pending in a few seconds."}


# ── Pending post ──────────────────────────────────────────────────────────────

@app.get("/api/posts/pending", tags=["Posts"])
def get_pending(_: str = Depends(auth.get_current_admin)):
    try:
        post = db.get_pending_post()
        if not post:
            return {"post": None, "message": "No post is awaiting approval."}
        return {"post": post}
    except Exception as e:
        logger.warning("Supabase unavailable for pending query: %s", e)
        return {"post": None, "message": "Database temporarily unavailable. Retrying…"}


# ── Post by ID ────────────────────────────────────────────────────────────────

@app.get("/api/posts/history", tags=["Posts"])
def get_history(_: str = Depends(auth.get_current_admin)):
    posts = db.get_recent_posts(days=7)
    return {"posts": posts, "count": len(posts)}


@app.get("/api/posts/{post_id}", tags=["Posts"])
def get_post(post_id: str, _: str = Depends(auth.get_current_admin)):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"post": post}


# ── Caption update ────────────────────────────────────────────────────────────

@app.patch("/api/posts/{post_id}/caption", tags=["Posts"])
def update_caption(
    post_id: str,
    req: UpdateCaptionRequest,
    _: str = Depends(auth.get_current_admin),
):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    updates = {}
    if req.caption  is not None: updates["caption"]  = req.caption
    if req.hashtags is not None: updates["hashtags"] = req.hashtags
    updated = db.update_post(post_id, updates)
    return {"post": updated, "message": "Caption updated."}


# ── Approve ───────────────────────────────────────────────────────────────────

def _run_publish(post_id: str):
    try:
        from meta_publisher import publish_post
        post = db.get_post_by_id(post_id)
        if not post:
            return

        fb_id, ig_id, error, resolved_image_url = publish_post(post)
        now = datetime.now(timezone.utc)
        updates = {
            "status":            "published" if (fb_id or ig_id) else "failed",
            "published_at":      now.isoformat(),
            "facebook_post_id":  fb_id,
            "instagram_post_id": ig_id,
            "error_message":     error,
            "expires_at":        (now + timedelta(days=7)).isoformat(),
        }
        if resolved_image_url:
            updates["image_url"] = resolved_image_url
        db.update_post(post_id, updates)
        logger.info("✅ Post %s published. FB=%s IG=%s", post_id, fb_id, ig_id)
    except Exception as e:
        db.update_post(post_id, {"status": "failed", "error_message": str(e)})
        logger.exception("❌ Publish failed for post %s: %s", post_id, e)


@app.post("/api/posts/{post_id}/approve", tags=["Posts"])
def approve_post(
    post_id: str,
    background_tasks: BackgroundTasks,
    _: str = Depends(auth.get_current_admin),
):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["status"] not in ("awaiting_approval", "generated"):
        raise HTTPException(status_code=400, detail=f"Post is in '{post['status']}' state — cannot approve.")

    db.update_post(post_id, {
        "status":      "approved",
        "approved_at": datetime.now(timezone.utc).isoformat(),
    })
    background_tasks.add_task(_run_publish, post_id)
    return {"message": "Post approved! Publishing to Instagram and Facebook …"}


# ── Reject ────────────────────────────────────────────────────────────────────

@app.post("/api/posts/{post_id}/reject", tags=["Posts"])
def reject_post(post_id: str, _: str = Depends(auth.get_current_admin)):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.update_post(post_id, {"status": "rejected"})
    return {"message": "Post rejected."}


# ── Clear Database ────────────────────────────────────────────────────────────

@app.delete("/api/posts/clear", tags=["Posts"])
def clear_database(_: str = Depends(auth.get_current_admin)):
    count = db.clear_all_posts()
    return {"message": f"Database cleared. Deleted {count} posts.", "count": count}


# ── Regenerate ────────────────────────────────────────────────────────────────

@app.post("/api/posts/{post_id}/regenerate", tags=["Posts"])
def regenerate_post(
    post_id: str,
    background_tasks: BackgroundTasks,
    _: str = Depends(auth.get_current_admin),
):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Mark old post as rejected
    db.update_post(post_id, {"status": "rejected"})

    # Kick off a new generation with the same post_type and subject
    background_tasks.add_task(
        _run_generation,
        post.get("post_type"),
        post.get("subject"),
        post.get("class_level"),
    )
    return {"message": "Regenerating post … Check /api/posts/pending shortly."}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
