"""
content_generator.py — AI post generation using NVIDIA and DeepSeek APIs.

NVIDIA handles cheap first-draft generation.
DeepSeek handles educational fact-checking and final review.
"""
from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from typing import Dict, Any, Optional

from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)

# ── Weekly content schedule ───────────────────────────────────────────────────
# Posts are auto-generated at 10 PM the night before for next-day review.
WEEKLY_SCHEDULE = {
    0: ("word_of_day",          "English",         None),    # Monday
    1: ("question_of_day",      "Mathematics",     None),    # Tuesday
    2: ("interesting_fact",     "Science",         None),    # Wednesday
    3: ("quiz_poll",            "History/GK",      None),    # Thursday
    4: ("motivational_quote",   "Student Life",    None),    # Friday
    5: ("trending_awareness",   "Exam Tips",       None),    # Saturday
    6: ("admission_post",       "Promotional",     None),    # Sunday
}

CLASS_LEVELS_ENGLISH = ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"]  # CBSE
CLASS_LEVELS_HINDI   = ["Class 9", "Class 10"]                                     # Bihar Board (BSEB)
CLASS_LEVELS = CLASS_LEVELS_ENGLISH  # kept for any direct references

# Brand constants
BRAND = {
    "name": "Edu Platform",
    "phone": "1234567890 / 9643557068",
    "website": "https://thebuniyaad.com",
    "address": "Janata Cinema Campus, Near Bhagat Singh Chowk, City, State – 841428",
    "courses": "CBSE / BSEB Classes 6–12 | JEE | NEET | BPSC",
}

HASHTAG_BASE = "#BuniyaadTheFoundation #BuniyaadCoaching #BiharEducation #StudyMotivation"


# ── LLM clients ──────────────────────────────────────────────────────────────

def _openrouter_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        timeout=10.0,
    )

def _groq_client() -> OpenAI:
    return OpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        timeout=10.0,
    )

def _nvidia_client() -> OpenAI:
    return OpenAI(
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        timeout=10.0,
    )

def _huggingface_client() -> OpenAI:
    return OpenAI(
        api_key=settings.huggingface_api_key,
        base_url=settings.huggingface_base_url,
        timeout=10.0,
    )


def _get_providers():
    """Yields (client, model, name) in priority order — preferred provider first, others as fallbacks."""
    preferred = settings.active_provider.lower().strip()

    # Build all available providers as (priority_order, client, model, name)
    all_providers = []
    if settings.nvidia_api_key:
        all_providers.append(("nvidia",       _nvidia_client(),      settings.nvidia_model,      "NVIDIA"))
    if settings.groq_api_key:
        all_providers.append(("groq",          _groq_client(),        settings.groq_model,        "Groq"))
    if settings.openrouter_api_key:
        all_providers.append(("openrouter",    _openrouter_client(),  settings.openrouter_model,  "OpenRouter"))
    if settings.huggingface_api_key:
        all_providers.append(("huggingface",   _huggingface_client(), settings.huggingface_model, "HuggingFace"))

    # Sort: preferred provider first, preserve insertion order for the rest
    preferred_first = [p for p in all_providers if p[0] == preferred]
    rest            = [p for p in all_providers if p[0] != preferred]

    for key, client, model, name in (preferred_first + rest):
        yield client, model, name

def _call_llm(system: str, user: str, max_tokens: int = 1024) -> str:
    """Generic LLM call with multi-provider fallback and error handling."""
    last_error = None

    for client, model, name in _get_providers():
        try:
            logger.info("Attempting generation with %s (%s)...", name, model)

            request_kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.7,
                "max_tokens": max_tokens,
            }

            if name == "OpenRouter":
                request_kwargs["extra_body"] = {
                    "provider": {
                        "sort": "latency"
                    }
                }

            response = client.chat.completions.create(**request_kwargs)

            message = response.choices[0].message
            content = getattr(message, "content", None)

            if not content or not content.strip():
                logger.warning(
                    "❌ %s returned empty content. finish_reason=%s, reasoning=%s",
                    name,
                    getattr(response.choices[0], "finish_reason", None),
                    getattr(message, "reasoning", None),
                )
                raise ValueError(f"{name} returned empty content")

            raw = content.strip()

            # Clean markdown fences and conversational filler
            if "```json" in raw:
                raw = raw.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in raw:
                raw = raw.split("```", 1)[1].split("```", 1)[0]

            raw = raw.strip()

            if "{" in raw:
                raw = raw[raw.find("{"):]

            if "}" in raw:
                raw = raw[:raw.rfind("}") + 1]

            return raw

        except Exception as e:
            logger.warning("❌ %s failed: %s", name, e)
            last_error = e
            continue

    logger.error("All LLM providers failed. Last error: %s", last_error)
    raise RuntimeError(f"All LLM providers failed: {last_error}")

# ── Post-type generators ──────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a social media content expert for Edu Platform, "
    "an educational coaching institute in City, State. "
    "Create engaging, accurate, and simple educational social media posts. "
    "Always respond with valid JSON only. No markdown fences."
)

SAFETY_RULES = (
    "Rules: (1) Educational answers must be 100% accurate. "
    "(2) Avoid political opinions, religious comparisons, offensive jokes. "
    "(3) Language must be simple and clear. "
    "(4) Promotional content should be honest."
)

HINDI_RULES = (
    "IMPORTANT LANGUAGE RULE: Write ALL text content (question, answer, explanation, caption, fact_title, fact_text, greeting_message, bullet_points, headline, quote) "
    "ENTIRELY in Hindi using Devanagari script. This is for Bihar Board (BSEB) students. "
    "Use simple, clear Hindi. "
    "NUMBERS & DIGITS RULE: Always use English/Arabic numerals (0, 1, 2, 3, 4, 5, 6, 7, 8, 9) for ALL numbers, dates, percentages, roll numbers, years, phone numbers, and class numbers. "
    "Do NOT use Devanagari numerals (१, २, ३ etc.). "
    "Only brand names, phone numbers, website URLs, and class/grade numbers should remain in English/Latin script."
)


def generate_question_of_day(subject: str, class_level: str, language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    prompt = f"""
Generate an engaging 'Question of the Day' social media post for {class_level} {subject}.

{SAFETY_RULES}
{lang_rule}
Do NOT use complex math notation. Keep it simple.

Return JSON with these exact keys:
{{
  "question": "The quiz question",
  "answer": "The correct answer",
  "explanation": "A 1-2 sentence simple explanation of why it is correct",
  "caption": "Full Instagram caption. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags as a single string",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Learn more with Buniyaad! Call: {BRAND['phone']} | {BRAND['website']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "question_of_day"
    data["subject"] = subject
    data["class_level"] = class_level
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #{subject.replace(' ', '')}".strip()
    return data


def generate_word_of_day() -> Dict[str, Any]:
    prompt = f"""
Generate an educational 'Word of the Day' social media post (English to Hindi vocabulary).

{SAFETY_RULES}

Return JSON with these exact keys:
{{
  "word": "An important English vocabulary word (useful for students)",
  "phonetic": "Pronunciation spelling (e.g. /əˈbæn.dən/)",
  "meaning": "Simple English meaning",
  "hindi_meaning": "Meaning in Hindi (Devanagari script)",
  "example_sentence": "A simple English sentence using the word",
  "caption": "Full Instagram caption explaining the word. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags as a single string",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Improve your vocabulary with Buniyaad! Call: {BRAND['phone']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "word_of_day"
    data["subject"] = "English"
    data["class_level"] = "All Classes"
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #WordOfTheDay #EnglishVocabulary".strip()
    return data


def generate_interesting_fact(subject: str, language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    intro = "क्या आप जानते हैं? 🤔" if language == "hindi" else "Did you know? 🤔"
    prompt = f"""
Generate an 'Interesting Fact' social media post about {subject}.

{SAFETY_RULES}
{lang_rule}

Return JSON with these exact keys:
{{
  "fact_title": "...",
  "fact_text": "Fact in 2-3 sentences",
  "caption": "Full Instagram caption starting with '{intro}'. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags as a single string",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Stay curious with Buniyaad! Call: {BRAND['phone']} | {BRAND['website']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "interesting_fact"
    data["subject"] = subject
    data["class_level"] = "All Classes"
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #DidYouKnow #Facts".strip()
    return data


def generate_festival_greeting(festival_name: str, language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    prompt = f"""
Generate a festival greeting social media post for {festival_name} for Buniyaad coaching institute.

{SAFETY_RULES}
{lang_rule}

Return JSON with these exact keys:
{{
  "greeting_message": "2-3 sentence warm greeting",
  "caption": "Full Instagram caption. Start with festival name. End with brand message.",
  "hashtags": "8-10 relevant hashtags",
  "suggestions": "One tip for admin about this post"
}}

Brand: "With warm wishes from Edu Platform. Call: {BRAND['phone']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "festival_greeting"
    data["subject"] = "Festival"
    data["class_level"] = "All"
    data["topic"] = festival_name
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE}".strip()
    return data


from duckduckgo_search import DDGS

def _fetch_latest_news(query: str) -> str:
    """Fetch top 3 news articles from the last 24 hours."""
    try:
        # DDGS news returns a list of dicts with title, body, url, date
        results = DDGS().news(keywords=query, timelimit="d", max_results=3)
        if not results:
            return ""
        return "\n".join([f"- {r.get('title')}: {r.get('body')}" for r in results])
    except Exception as e:
        logger.error("DDGS news search failed: %s", e)
        return ""

def generate_trending_awareness(subject: str, language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    news_text = _fetch_latest_news(f"{subject} exam dates updates India")
    news_prompt = f"Live News from last 24hrs:\n{news_text}\nUse this live news if it's important, otherwise give general tips." if news_text else "Focus on general exam tips, prep strategies, and motivation."

    prompt = f"""
Generate an 'Exam & Trending Awareness' social media post about {subject}.
{news_prompt}

{SAFETY_RULES}
{lang_rule}

Return JSON with these exact keys:
{{
  "headline": "Catchy headline",
  "bullet_points": "3-4 key points/tips formatted as a single string with bullets",
  "caption": "Full Instagram caption. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags as a single string",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Prepare smart with Buniyaad! Call: {BRAND['phone']} | {BRAND['website']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "trending_awareness"
    data["subject"] = subject
    data["class_level"] = "All Classes"
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #ExamTips #Education".strip()
    return data

def check_and_generate_trending_news(subject: str, language: str = "english") -> Optional[Dict[str, Any]]:
    """Evaluates live news and ONLY generates a post if there is breaking news."""
    news_text = _fetch_latest_news(f"{subject} exam dates news updates India")
    if not news_text:
        return None
        
    lang_rule = HINDI_RULES if language == "hindi" else ""
    prompt = f"""
Here is the latest news about {subject} from the last 24 hours:
{news_text}

Analyze this news. Does it contain any major, breaking announcement like an exam date release, syllabus change, or critical update for students?
If NO (e.g. it's just minor noise, opinions, or nothing new), reply with exactly this JSON: {{"skip": true}}

If YES, generate an 'Exam & Trending Awareness' social media post to inform students immediately.
{SAFETY_RULES}
{lang_rule}

Return JSON with these exact keys:
{{
  "headline": "Catchy breaking news headline",
  "bullet_points": "3-4 key points formatted as a single string with bullets",
  "caption": "Full Instagram caption summarizing the news. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags as a single string",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Stay updated with Buniyaad! Call: {BRAND['phone']} | {BRAND['website']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    if data.get("skip") == True:
        return None
        
    data["post_type"] = "trending_awareness"
    data["subject"] = subject
    data["class_level"] = "All Classes"
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #ExamUpdates".strip()
    return data

def generate_quiz_poll(subject: str, class_level: str, language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    prompt = f"""
Generate an engaging 'Quiz / Poll' social media post for {class_level} {subject}.

{SAFETY_RULES}
{lang_rule}
Do NOT use complex math notation. Keep it simple.

Return JSON with these exact keys:
{{
  "question": "The quiz question",
  "option_a": "First option",
  "option_b": "Second option",
  "option_c": "Third option",
  "option_d": "Fourth option",
  "correct_answer": "Which option is correct (A, B, C, or D) and why (short explanation)",
  "caption": "Instagram caption encouraging students to comment their answer. Do NOT reveal the answer in the caption! End with brand CTA.",
  "hashtags": "8-10 relevant hashtags",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Test your knowledge with Buniyaad! Call: {BRAND['phone']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "quiz_poll"
    data["subject"] = subject
    data["class_level"] = class_level
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #QuizTime #DailyQuiz".strip()
    return data

def generate_motivational_quote(language: str = "english") -> Dict[str, Any]:
    lang_rule = HINDI_RULES if language == "hindi" else ""
    prompt = f"""
Generate an educational 'Motivational Quote' social media post for students.

{SAFETY_RULES}
{lang_rule}

Return JSON with these exact keys:
{{
  "quote": "The motivational quote",
  "author": "Author of the quote (or 'Anonymous')",
  "caption": "Instagram caption expanding on the quote's meaning for students. End with brand CTA.",
  "hashtags": "8-10 relevant hashtags",
  "suggestions": "One tip for admin about this post"
}}

Brand CTA: "Achieve your dreams with Buniyaad! Call: {BRAND['phone']}"
"""
    raw = _call_llm(SYSTEM_PROMPT, prompt)
    data = json.loads(raw, strict=False)
    data["post_type"] = "motivational_quote"
    data["subject"] = "Motivation"
    data["class_level"] = "All Classes"
    data["language"] = language
    data["hashtags"] = f"{data.get('hashtags', '')} {HASHTAG_BASE} #Motivation #StudentLife".strip()
    return data


# ── Fact-checking via DeepSeek ────────────────────────────────────────────────

def fact_check(post_data: Dict[str, Any]) -> str:
    """Returns 'verified', 'unverified', or 'failed'."""
    if post_data.get("post_type") not in ("question_of_day", "interesting_fact", "quiz_poll"):
        return "verified"  # Non-educational posts skip fact-check

    groq = _groq_client()
    question = post_data.get("question", post_data.get("fact_text", ""))
    answer   = post_data.get("answer", post_data.get("fact_title", post_data.get("correct_answer", "")))

    prompt = f"""
Verify this educational content for accuracy. Is this information correct?

Content: {question}
Answer/Fact: {answer}

Respond with JSON only:
{{"is_accurate": true/false, "confidence": "high/medium/low", "note": "brief explanation"}}
"""
    try:
        raw = _call_llm("You are a fact-checking expert.", prompt, max_tokens=256)
        result = json.loads(raw, strict=False)
        if result.get("is_accurate") and result.get("confidence") in ("high", "medium"):
            return "verified"
        return "unverified"
    except Exception as e:
        logger.warning("Fact-check failed: %s", e)
        return "failed"


# ── Daily post orchestrator ───────────────────────────────────────────────────

def generate_daily_post(
    post_type: Optional[str] = None,
    subject: Optional[str] = None,
    class_level: Optional[str] = None,
    language: str = "english",
    for_tomorrow: bool = False,
) -> Dict[str, Any]:
    """
    Generate today's (or tomorrow's) post. If post_type is None, pick
    automatically from the weekly schedule.
    language: 'english' (default) or 'hindi' (Bihar Board 9-10)
    for_tomorrow: if True, use tomorrow's weekday from the schedule.
    """
    if post_type is None:
        from datetime import timedelta
        target_date = datetime.now()
        if for_tomorrow:
            target_date += timedelta(days=1)
        weekday = target_date.weekday()
        scheduled_type, scheduled_subject, _ = WEEKLY_SCHEDULE[weekday]
        post_type = scheduled_type
        subject   = subject or scheduled_subject

    if class_level is None:
        if language == "hindi":
            class_level = random.choice(CLASS_LEVELS_HINDI)   # Class 9 or 10 — Bihar Board
        else:
            class_level = random.choice(CLASS_LEVELS_ENGLISH) # Class 6-10 — CBSE

    logger.info("Generating post: type=%s subject=%s class=%s language=%s", post_type, subject, class_level, language)

    if post_type == "question_of_day":
        data = generate_question_of_day(subject or "Science", class_level, language)
    elif post_type == "word_of_day":
        data = generate_word_of_day()  # Always English — word + Hindi meaning
    elif post_type == "interesting_fact":
        data = generate_interesting_fact(subject or "Science", language)
    elif post_type == "festival_greeting":
        data = generate_festival_greeting(subject or "Festival", language)
    elif post_type == "trending_awareness":
        data = generate_trending_awareness(subject or "Exam Tips", language)
    elif post_type == "quiz_poll":
        data = generate_quiz_poll(subject or "Science", class_level, language)
    elif post_type == "motivational_quote":
        data = generate_motivational_quote(language)
    else:
        data = generate_question_of_day(subject or "Science", class_level, language)

    # Fact-check is now done in parallel with image generation by the caller
    data["status"] = "awaiting_approval"

    return data
