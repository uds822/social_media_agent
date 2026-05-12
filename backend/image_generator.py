"""
image_generator.py — Playwright HTML-to-image renderer.

Pipeline:
  1. Pick HTML template by post_type
  2. Inject LLM content into template placeholders
  3. Playwright (headless Chromium) screenshots at 1080×1080
  4. Upload PNG to Cloudinary → return secure URL
"""
from __future__ import annotations

import base64
import logging
import pathlib
from typing import Dict, Any, Optional

import cloudinary
import cloudinary.uploader

from config import settings

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = pathlib.Path(__file__).parent
TMPL_DIR   = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH  = ASSETS_DIR / "logo.png"

# ── Cloudinary ────────────────────────────────────────────────────────────────
def _configure_cloudinary():
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

# ── Template mapping ──────────────────────────────────────────────────────────
TEMPLATE_MAP = {
    "word_of_day":        "word_of_day.html",
    "question_of_day":    "question_of_day.html",
    "interesting_fact":   "science_fact.html",  # overridden per subject below
    "festival_greeting":  "festival.html",
    "trending_awareness": "trending.html",
    "quiz_poll":          "quiz.html",
    "motivational_quote": "quote.html",
}

def _pick_template(post_data: Dict[str, Any]) -> pathlib.Path:
    post_type = post_data.get("post_type", "interesting_fact")
    subject   = post_data.get("subject", "")

    if post_type == "interesting_fact":
        if "history" in subject.lower() or "gk" in subject.lower():
            tmpl = "history_fact.html"
        else:
            tmpl = "science_fact.html"
    else:
        tmpl = TEMPLATE_MAP.get(post_type, "science_fact.html")

    path = TMPL_DIR / tmpl
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path

# ── Logo as base64 data-URI ───────────────────────────────────────────────────
def _logo_data_uri() -> str:
    if LOGO_PATH.exists():
        b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f"data:image/png;base64,{b64}"
    logger.warning("Logo not found at %s — header will show without image", LOGO_PATH)
    return ""

# ── Content field mappings ────────────────────────────────────────────────────
def _build_replacements(post_data: Dict[str, Any]) -> Dict[str, str]:
    """Map post_data fields → template {{PLACEHOLDER}} values."""
    p = post_data
    subject   = p.get("subject", "")
    post_type = p.get("post_type", "")

    # Science / History fact
    fact_body = p.get("fact_text", "")
    if not fact_body:
        # Try to build from caption if fact_text missing
        caption = p.get("caption", "")
        fact_body = caption[:500] if caption else "—"

    # Question of the day
    explanation = p.get("explanation", "")

    # Word of day - phonetic may be missing from LLM response
    phonetic = p.get("phonetic", p.get("pronunciation", ""))

    # Festival topic
    festival_topic = p.get("topic", subject)
    greeting       = p.get("greeting_message", p.get("caption", "")[:300])

    # Fact title fallback
    fact_title = p.get("fact_title", p.get("headline", "Did You Know?"))

    return {
        "LOGO_PATH":         _logo_data_uri(),
        # Science / History
        "FACT_TITLE":        _safe(fact_title),
        "FACT_BODY":         _safe(fact_body),
        "SUBJECT":           _safe(subject),
        # Word of day
        "WORD":              _safe(p.get("word", "")).upper(),
        "PHONETIC":          _safe(phonetic),
        "MEANING":           _safe(p.get("meaning", "")),
        "HINDI_MEANING":     _safe(p.get("hindi_meaning", "")),
        "EXAMPLE_SENTENCE":  _safe(p.get("example_sentence", "")),
        # Question of day
        "CLASS_LEVEL":       _safe(p.get("class_level", "All Classes")),
        "QUESTION":          _safe(p.get("question", "")),
        "ANSWER":            _safe(p.get("answer", "")),
        "EXPLANATION":       _safe(explanation),
        # Festival
        "FESTIVAL_TOPIC":    _safe(festival_topic),
        "GREETING_MESSAGE":  _safe(greeting),
        # Trending Awareness
        "HEADLINE":          _safe(p.get("headline", "")),
        "BULLET_POINTS":     _safe(p.get("bullet_points", "")),
        # Quiz / Poll
        "OPTION_A":          _safe(p.get("option_a", "")),
        "OPTION_B":          _safe(p.get("option_b", "")),
        "OPTION_C":          _safe(p.get("option_c", "")),
        "OPTION_D":          _safe(p.get("option_d", "")),
        # Motivational Quote
        "QUOTE":             _safe(p.get("quote", "")),
        "AUTHOR":            _safe(p.get("author", "")),
    }

def _safe(text: Any) -> str:
    """Strip HTML special chars and emoji that can crash the renderer."""
    s = str(text or "")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s

# ── Playwright render ─────────────────────────────────────────────────────────
def _render_html_to_png(html: str) -> bytes:
    import tempfile, subprocess, os, sys
    with tempfile.TemporaryDirectory() as d:
        html_file = os.path.join(d, "temp.html").replace("\\", "/")
        png_file = os.path.join(d, "temp.png")
        script_file = os.path.join(d, "script.py")
        
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)
            
        script = f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])
    page = browser.new_page(viewport={{"width": 1080, "height": 1080}})
    page.goto(f"file:///{html_file}")
    page.wait_for_timeout(1500)
    page.screenshot(path=r"{png_file}", full_page=False)
    browser.close()
"""
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
            
        res = subprocess.run([sys.executable, script_file], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Playwright subprocess failed: {res.stderr}")
            
        with open(png_file, "rb") as f:
            return f.read()

# ── Public API ────────────────────────────────────────────────────────────────
def generate_and_upload_image(post_data: Dict[str, Any]) -> Optional[str]:
    """
    Render the appropriate HTML template with LLM content,
    screenshot it, upload to Cloudinary, return the URL.
    """
    try:
        _configure_cloudinary()

        tmpl_path    = _pick_template(post_data)
        tmpl_html    = tmpl_path.read_text(encoding="utf-8")
        replacements = _build_replacements(post_data)

        # Apply all placeholder replacements
        html = tmpl_html
        for key, value in replacements.items():
            html = html.replace("{{" + key + "}}", value)

        logger.info("Rendering template: %s", tmpl_path.name)
        png_bytes = _render_html_to_png(html)
        logger.info("Rendered: %d bytes", len(png_bytes))

        result = cloudinary.uploader.upload(
            png_bytes,
            folder="buniyaad/posts",
            resource_type="image",
            format="jpg",
            transformation=[{"quality": "auto:best"}],
        )
        url = result.get("secure_url")
        logger.info("Uploaded to Cloudinary: %s", url)
        return url

    except Exception as e:
        logger.error("Image generation failed: %s", e, exc_info=True)
        return None
