"""
config.py — Centralised settings via pydantic-settings.
All values are loaded from the .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Admin
    admin_username: str = "admin"
    admin_password: str = "buniyaad2024"
    backup_codes: str = ""
    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    # Groq
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"

    # NVIDIA
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    # Hugging Face
    huggingface_api_key: str = ""
    huggingface_base_url: str = "https://api-inference.huggingface.co/models"
    huggingface_model: str = "meta-llama/Llama-3.3-70B-Instruct"

    # Active provider preference — tried FIRST, others are fallbacks
    # Valid values: openrouter | groq | nvidia | huggingface
    active_provider: str = "nvidia"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Meta
    facebook_page_id: str = ""
    facebook_page_access_token: str = ""
    instagram_business_account_id: str = ""

    # Scheduler (auto-generates post at this time)
    daily_post_hour: int = 22
    daily_post_minute: int = 40

    # Send morning Telegram notification at this time
    notification_hour: int = 22
    notification_minute: int = 42

    # Telegram Notification
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # App
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
