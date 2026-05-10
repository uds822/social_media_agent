# 🎓 EduPlatform Social Media Agent — Complete Setup Guide

> **Everything you need to register, configure, and run the system.**

---

## 📦 What Was Built

```
Social_media_agent/
├── backend/
│   ├── main.py              ← FastAPI server (all REST endpoints)
│   ├── content_generator.py ← NVIDIA + DeepSeek AI content generation
│   ├── image_generator.py   ← Pillow image templates + Cloudinary upload
│   ├── meta_publisher.py    ← Facebook Page + Instagram API publisher
│   ├── database.py          ← Supabase CRUD helpers
│   ├── auth.py              ← JWT login
│   ├── scheduler.py         ← Daily auto-generation + 7-day cleanup
│   ├── config.py            ← All settings from .env
│   ├── requirements.txt     ← Python dependencies
│   └── .env.example         ← Template — copy to .env and fill in keys
├── frontend/
│   ├── index.html           ← Admin dashboard (works on phone browser)
│   ├── style.css            ← Dark glassmorphism UI
│   └── app.js               ← Dashboard logic
├── database/
│   └── migration.sql        ← Run once in Supabase SQL Editor
├── start_backend.bat        ← Double-click to start backend
├── start_frontend.bat       ← Double-click to open dashboard
└── SETUP_GUIDE.md           ← This file
```

---

## ⚡ Quick Start (after all keys are set up)

1. Copy `backend\.env.example` → `backend\.env` and fill in all keys
2. Double-click `start_backend.bat`
3. Double-click `start_frontend.bat`
4. Open `http://localhost:3000` in your browser
5. Login with `admin` / your password
6. Click **Generate New** → wait ~15 seconds → **Approve & Publish**

---

## 🔑 Step 1 — Register for These 5 Services

### 1. NVIDIA LLM API — FREE

**Used for:** Draft captions, hashtags, word-of-the-day, facts

| | |
|---|---|
| Link | https://build.nvidia.com |
| Cost | **FREE** ($50 credit on signup) |
| Time | ~5 minutes |

**Steps:**
1. Go to **https://build.nvidia.com**
2. Click **"Sign Up"** — use Google or email
3. After login → click your profile icon (top right) → **"API Key"**
4. Copy the key starting with `nvapi-...`
5. Open `backend\.env` and paste:
   ```
   NVIDIA_API_KEY=nvapi-your-key-here
   ```

> ✅ $50 free credit = months of daily posts at current usage

---

### 2. DeepSeek API — Very Cheap

**Used for:** Fact-checking educational answers (maths, science questions)

| | |
|---|---|
| Link | https://platform.deepseek.com |
| Cost | ~₹10–20/month |
| Time | ~5 minutes |

**Steps:**
1. Go to **https://platform.deepseek.com**
2. Click **"Sign Up"** → verify email
3. Go to **"Top Up"** → add **$5** (enough for months)
4. Go to **"API Keys"** → **"Create new key"**
5. Copy key starting with `sk-...`
6. Paste into `backend\.env`:
   ```
   DEEPSEEK_API_KEY=sk-your-key-here
   ```

> 💡 $5 = ~5000 fact-check calls. Each daily post uses only 1–2 calls.

---

### 3. Supabase — FREE PostgreSQL Database

**Used for:** Storing all posts, approval status, 7-day backup, cleanup

| | |
|---|---|
| Link | https://supabase.com |
| Cost | **FREE** (500MB storage) |
| Time | ~10 minutes |

**Steps:**
1. Go to **https://supabase.com** → **"Start your project"**
2. Sign up with GitHub or email
3. Click **"New Project"**:
   - Name: `eduplatform-agent`
   - Database password: (save it somewhere safe)
   - Region: **South Asia (ap-south-1)** — closest to Bihar
4. Wait ~2 minutes for project to initialise
5. Go to **Settings → API** (left sidebar)
6. Copy these two values:
   - **Project URL** → paste as `SUPABASE_URL`
   - **anon / public key** → paste as `SUPABASE_ANON_KEY`
7. Go to **SQL Editor → New Query**
8. Open `database\migration.sql` from your project folder
9. Copy its entire content and paste into the SQL Editor
10. Click **"Run"** — you should see: `posts table created successfully`

> ✅ Free tier: 500MB storage, 2GB bandwidth/month

---

### 4. Cloudinary — FREE Image Storage

**Used for:** Storing generated post images and giving Meta API a public URL

| | |
|---|---|
| Link | https://cloudinary.com |
| Cost | **FREE** (25 credits/month) |
| Time | ~5 minutes |

**Steps:**
1. Go to **https://cloudinary.com** → **"Sign Up For Free"**
2. After login → go to your **Dashboard** (home page)
3. Copy all three values at the top:
   - **Cloud Name** → paste as `CLOUDINARY_CLOUD_NAME`
   - **API Key** → paste as `CLOUDINARY_API_KEY`
   - **API Secret** → paste as `CLOUDINARY_API_SECRET`

> ✅ Each daily post image uses ~0.001 credits. Free tier lasts 25,000 images.

---

### 5. Meta Developer (Facebook + Instagram) — START THIS TODAY

**Used for:** Publishing posts to Facebook Page and Instagram

| | |
|---|---|
| Link | https://developers.facebook.com |
| Cost | **FREE** |
| Time | Setup: 30 min. App Review: **1–2 weeks** |

> ⚠️ **Start this immediately. Meta App Review can take up to 2 weeks.**

**Pre-requirements before you start:**
- Instagram account is **Business or Creator** (not personal)
- Instagram is **linked to your EduPlatform Facebook Page**
- You have **Admin access** to the Facebook Page

**Step A: Convert Instagram to Business Account**
1. Open Instagram → Profile → Menu (☰) → Settings
2. Tap **"Account"** → **"Switch to Professional Account"**
3. Choose **"Business"** → Category: **"Education"**
4. Connect to your EduPlatform Facebook Page

**Step B: Create Meta Developer Account**
1. Go to **https://developers.facebook.com**
2. Click **"Get Started"** → log in with Facebook
3. Verify identity with phone number → accept developer terms

**Step C: Create a Meta App**
1. Dashboard → **"Create App"**
2. Use case: **"Other"** → App type: **"Business"**
3. App name: `EduPlatform Social Agent`
4. Click **"Create App"**

**Step D: Add Products**
1. Inside your app → **"+ Add Product"**
2. Add **"Instagram Graph API"** → Set Up
3. Add **"Facebook Login"** → Set Up → Web

**Step E: Get Page Access Token**
1. Go to **https://developers.facebook.com/tools/explorer**
2. Select your app → Select your **EduPlatform Facebook Page**
3. Add permissions: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`
4. Click **"Generate Access Token"** → approve the popup
5. Copy the token → paste as `FACEBOOK_PAGE_ACCESS_TOKEN`
6. Get your Page ID from your Facebook Page → "About" section
7. Paste as `FACEBOOK_PAGE_ID`

**Step F: Get Instagram Business Account ID**
1. In Graph API Explorer, run: `/me/accounts` → copy your page `id`
2. Then run: `/{page-id}?fields=instagram_business_account`
3. Copy the returned `id` → paste as `INSTAGRAM_BUSINESS_ACCOUNT_ID`

**Step G: App Review (for production)**
- Go to your app → App Review → Permissions and Features
- Request: `instagram_content_publish`, `pages_manage_posts`
- Submit with usage screenshots → wait 1–2 weeks

> 💡 While waiting for review, you can still test posting to your own accounts.

---

## 🚀 Step 2 — Local Setup

### Install Dependencies

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Configure .env

```powershell
copy .env.example .env
notepad .env
```

**Checklist for .env:**
- [ ] `ADMIN_PASSWORD` — change from default
- [ ] `JWT_SECRET` — run: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `NVIDIA_API_KEY`
- [ ] `DEEPSEEK_API_KEY`
- [ ] `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- [ ] `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- [ ] `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`
- [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID`

### Run Database Migration

Supabase Dashboard → SQL Editor → New Query → paste `database\migration.sql` → Run

### Start Backend

Double-click `start_backend.bat`

- Backend URL: **http://localhost:8000**
- API Docs (Swagger): **http://localhost:8000/docs**

### Start Frontend

Double-click `start_frontend.bat`

- Dashboard: **http://localhost:3000**

---

## 📱 Use on Your Phone (No App Install Needed)

1. Find your PC's local IP: run `ipconfig` → look for `IPv4 Address` (e.g., `192.168.1.10`)
2. Phone must be on the **same WiFi** as your PC
3. Open phone browser → go to `http://192.168.1.10:3000`
4. Dashboard Settings tab → set Backend URL to `http://192.168.1.10:8000`
5. **Add to Home Screen** for app-like feel:
   - Android Chrome → Menu (⋮) → "Add to Home screen"

---

## 📋 Daily Workflow

```
7:00 AM IST — Scheduler auto-generates today's post
      ↓
Open dashboard on phone
      ↓
Review: Image | Caption | Hashtags | AI Suggestions | Fact-check status
      ↓
Edit caption if needed (tap ✏️ icon)
      ↓
Tap "Approve & Publish"
      ↓
System posts to Instagram + Facebook automatically
      ↓
Post backed up for 7 days → then auto-deleted
```

---

## 💰 Expected Monthly Cost

| Service | Cost |
|---|---|
| NVIDIA LLM | **Free** ($50 credit) |
| DeepSeek | **~₹10–20** |
| Supabase | **Free** |
| Cloudinary | **Free** |
| Meta API | **Free** |
| Hosting (your PC) | **Free** |
| **Total** | **~₹10–20/month** |

> Cloud hosting: Render.com free tier (₹0) or Railway (~₹400–800/month for always-on)

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| "No post waiting" | Click "Generate New" or wait for 7 AM scheduler |
| Image not loading | Check Cloudinary credentials in `.env` |
| "LLM call failed" | Check NVIDIA and DeepSeek API keys in `.env` |
| "Meta publish failed" | Access token expired — refresh it in Graph API Explorer |
| Can't login | Check `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` |
| Phone can't reach backend | Use PC's local IP instead of `localhost` |
| Backend won't start | Make sure `.env` file exists in the `backend/` folder |

---

## ⚠️ Security Reminders

1. **Never share your `.env` file** — it has all your secret keys
2. **Never commit `.env` to GitHub** — add it to `.gitignore`
3. **Meta Access Token expires every 60 days** — refresh it from Graph API Explorer
4. **Change default password** — update `ADMIN_PASSWORD` in `.env`
5. **Change JWT_SECRET** — use a random 32-character hex string

---

## 🔮 What to Add After MVP

1. Festival calendar — auto-detect upcoming festivals
2. WhatsApp approval — send post preview via WhatsApp
3. Push notifications — notify phone when post is ready
4. Analytics dashboard — track reach, likes, comments
5. React Native APK — proper installable Android app
6. Reels scripts — generate short video scripts
7. Auto-refresh Meta token — so it never expires
8. Cloud hosting on Render/Railway — run 24/7 without your PC
