# 🤖 Autonomous Social Media Agent

> AI-powered daily content generation, branded image creation, and one-tap publishing to platforms like Instagram & Facebook.

## 🚀 Overview

The **Autonomous Social Media Agent** is an end-to-end automation platform designed to streamline social media presence. It seamlessly orchestrates content generation, fact-checking, graphics rendering, and direct platform publishing. This platform supports dynamic prompts, multi-language content, and robust API fallbacks.

## ⚡ Quick Start

1. `cd backend && cp .env.example .env` — Fill in your API keys.
2. `start_backend.bat` — Starts the FastAPI backend server on port 8000.
3. `start_frontend.bat` — Serves the admin dashboard on port 3000.
4. Open `http://localhost:3000` in your browser.

## 🛠️ Stack

| Layer           | Technology                              |
|-----------------|-----------------------------------------|
| **Backend**     | FastAPI + Python 3.12                   |
| **AI (Drafts)** | NVIDIA LLM API / Gemini                 |
| **AI (Review)** | DeepSeek API                            |
| **Database**    | Supabase PostgreSQL                     |
| **Images**      | Pillow + Cloudinary                     |
| **Publishing**  | Meta Graph API                          |
| **Admin UI**    | Vanilla HTML/CSS/JS (Mobile-Friendly)   |

## 📖 Setup Guide

See `SETUP_GUIDE.md` for full API registration steps.
