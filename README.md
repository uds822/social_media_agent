# 🤖 Autonomous Social Media Agent

An AI-powered, autonomous social media management system designed to generate, format, fact-check, and publish daily content across Instagram and Facebook. It includes a complete backend pipeline, an administrative approval dashboard, and automated image generation using customizable templates.

## ✨ Features

- **Automated Content Generation:** Uses advanced LLM integrations (NVIDIA LLM API & DeepSeek) to generate contextual posts in various categories (e.g., educational facts, trending news, quizzes, quotes, and word of the day).
- **Multi-language Support:** Automatically generates content in both English and regional languages (e.g., Hindi) based on the target audience.
- **Fact-Checking Pipeline:** Ensures the reliability of generated content using secondary AI verification.
- **Branded Image Generation:** Dynamically generates post creatives using HTML/CSS templates and Pillow, then uploads them to Cloudinary.
- **One-Tap Publishing:** Integrates with the Meta Graph API to instantly publish approved content directly to linked Facebook and Instagram accounts.
- **Admin Dashboard:** A responsive, mobile-friendly Vanilla JS/HTML/CSS dashboard to review, edit, approve, or reject AI-generated drafts.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- A Supabase account for PostgreSQL database
- Cloudinary account for image hosting
- Meta Developer account for Facebook/Instagram Graph API
- API keys for NVIDIA LLM and DeepSeek

### Setup

1. **Backend Configuration:**
   ```bash
   cd backend
   pip install -r requirements.txt
   copy .env.example .env
   # Open .env and fill in your API keys (Supabase, Meta, Cloudinary, LLMs)
   ```

2. **Start the Backend:**
   Run the backend FastAPI server (runs on port 8000 by default):
   ```bash
   start_backend.bat
   ```

3. **Start the Frontend Dashboard:**
   Serve the frontend UI (runs on port 3000 by default):
   ```bash
   start_frontend.bat
   ```
   Open `http://localhost:3000` in your web browser.

## 📚 Documentation
For comprehensive instructions on setting up your Meta Developer app, linking Instagram, and configuring the database, refer to the `SETUP_GUIDE.md` file.

## 🛠 Technology Stack

| Component | Technology |
|---|---|
| **Backend** | FastAPI + Python 3.12 |
| **AI Draft Generation** | NVIDIA LLM API |
| **AI Fact-Checking** | DeepSeek API |
| **Database** | Supabase (PostgreSQL) |
| **Image Processing** | Pillow + HTML/CSS Templates + Cloudinary |
| **Social Publishing** | Meta Graph API (Facebook & Instagram) |
| **Admin UI** | Vanilla HTML/CSS/JS (Mobile-responsive) |

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License
This project is licensed under the MIT License.
