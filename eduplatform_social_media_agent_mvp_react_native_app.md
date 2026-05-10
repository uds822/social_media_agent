# Edu Platform  
# Social Media Agent MVP Plan – React Native App Version

## 1. MVP Goal

Build a simple approval-based AI social media agent for **Edu Platform**.

The app will generate daily posts for Instagram and Facebook, create branded images, show the generated post to the admin inside a **React Native mobile app**, and publish only after approval.

The MVP should follow this core flow:

```text
Generate Post → Show in React Native App → Admin Approves → Publish to Instagram/Facebook → Keep 7 Days Backup
```

The system should **not** start as a big social media management platform. It should be a simple personal/admin mobile app.

---

## 2. Business Details

### Coaching Name

**Edu Platform**

### Address

Janata Cinema Campus, Near Bhagat Singh Chowk, City, State – 841428

### Contact Numbers

- 1234567890
- 9643557068

### Website

https://theeduplatform.com

### Courses

- CBSE / BSEB Classes 6–12
- JEE
- NEET
- BPSC

---

## 3. Final MVP Direction

Based on the current plan, the MVP should be:

```text
A simple React Native Android admin app for approving AI-generated Instagram/Facebook posts.
```

The admin will only see:

- Generated post image
- Caption
- Hashtags
- Suggestions
- Approve button
- Reject button
- Regenerate button
- Edit option

The app does not need:

- Complex analytics
- Full content archive
- Large calendar system
- CRM
- DM automation
- Comment automation
- Multi-user workflow
- Advanced social media management features

---

## 4. Mobile App Decision

You want a phone app and do not want to upload it to the Play Store.

This is possible using a React Native Android APK.

---

## 5. React Native App – Recommended

The MVP should be built as a **React Native Android app**.

React Native allows building a real mobile app using JavaScript/TypeScript and React-style development.

For this MVP, the app can be built and installed directly on your Android phone as an APK, without publishing on the Play Store.

### React Native APK Flow

```text
Build React Native app
↓
Generate Android APK
↓
Send APK to phone
↓
Allow install from unknown sources
↓
Install app
↓
Use privately
```

### Why React Native Is Good for This MVP

- Real Android app
- No Play Store required
- Good mobile user experience
- Works well for approval workflows
- Easy to build if developer knows React/JavaScript
- Can later be converted into a Play Store app if needed
- Can support push notifications later
- Can support camera/file access later if required

### Recommended React Native Setup

Recommended approach:

```text
React Native + Expo
```

or

```text
React Native CLI
```

For faster MVP development, use:

```text
Expo
```

Expo can help build Android APK/AAB more easily and makes development faster.

---

## 6. APK Installation Without Play Store

An **APK** is the Android installation file.

Like Windows uses `.exe`, Android uses `.apk`.

Example:

```text
eduplatform-admin.apk
```

You can install this APK directly on your Android phone without Play Store. This is called **sideloading**.

### APK Installation Flow

```text
Generate APK file
↓
Send APK to phone
↓
Open APK on phone
↓
Allow install from unknown sources
↓
Tap Install
↓
Use app privately
```

### How to Install APK on Phone

1. Generate the APK file.
2. Send it to the phone using WhatsApp, Google Drive, USB cable, or email.
3. Open the APK file on the phone.
4. Android will ask permission to install unknown apps.
5. Allow permission for that source.
6. Tap install.
7. App appears on the phone like a normal app.

### APK Pros

- No Play Store needed
- Private personal use possible
- Real Android app experience
- Good for phone-only workflow
- Can be shared with selected staff manually

### APK Cons

- Works mainly for Android
- User must allow unknown app installation
- Updates are manual
- Every new version requires new APK installation
- iPhone installation is not simple without App Store/TestFlight/Apple Developer setup

### Important Update Note

Since the app will not be on Play Store:

```text
Every new version must be installed manually as a new APK.
```

---

## 7. App Platform Decision

For this MVP:

```text
Main app: React Native Android APK
No Play Store upload
Private installation only
```

Do not build PWA as the main app.

PWA can be considered later only as a backup option.

---

## 8. MVP Scope

### Included in MVP

The MVP should include:

1. Daily post idea generation
2. Educational content generation
3. Caption generation
4. Hashtag generation
5. Suggestions for improvement
6. Fact-checking for educational posts
7. Template-based image generation
8. React Native Android admin app
9. Edit caption before approval
10. Regenerate post option
11. Publish to Instagram professional account
12. Publish to Facebook Page
13. Keep only 7 days backup

### Not Included in MVP

These should be added later, not in MVP:

1. Auto-reply to comments
2. Auto-reply to DMs
3. WhatsApp enquiry automation
4. Advanced analytics
5. Competitor analysis
6. Reels video generation
7. Fully automatic posting without approval
8. Student lead management CRM
9. Paid ads automation
10. Long-term full post archive
11. iOS app release

---

## 9. Simple MVP Workflow

```text
Daily Scheduler
      ↓
AI Content Generator
      ↓
Fact Checker
      ↓
Image Generator
      ↓
React Native Admin App
      ↓
Admin Approves
      ↓
Meta API Posting
      ↓
Keep 7 Days Backup
```

---

## 10. React Native App Screens

The mobile app should be very simple.

### Screen 1: Login

Admin logs in with username/password or magic link.

### Screen 2: Today’s Post

Shows:

- Generated image
- Caption
- Hashtags
- Suggestions
- Fact-check status
- Post type
- Subject
- Class level

Buttons:

```text
Approve and Post
Edit Caption
Regenerate
Reject
```

### Screen 3: Edit Caption

Admin can edit:

- Caption
- Hashtags
- CTA text

### Screen 4: Last 7 Days Backup

Shows only recent posts from the last 7 days.

Fields:

- Date
- Image
- Caption
- Status
- Platform
- Published time

### Screen 5: Settings

Basic settings:

- Brand phone number
- Website
- Posting time
- Meta account connection status
- LLM API status

---

## 11. Approval Method

Use the React Native mobile app as the main approval system.

### Recommended Approval Method

```text
React Native Android app
```

### Why

- Handy phone app
- No Play Store required
- Easy for admin to approve posts
- App can be used privately
- Better mobile experience than a browser-only app

---

## 12. Image API Decision

The app will use template-based image generation.

Since admin only approves posts and does not need to visually edit templates every day, the best option is:

```text
HCTI / HTML-CSS-to-Image + Cloudinary
```

### Why HCTI / HTML-CSS-to-Image

- Good for fixed templates
- Developer-friendly
- Cheaper than visual design tools
- Easy to control layout
- Consistent brand design
- Better for automated educational posts

### When to Use APITemplate.io Instead

Use APITemplate.io only if:

- Non-technical staff will edit templates visually
- You want an easier visual template builder
- You do not want developer-managed HTML/CSS templates

### Final Recommendation

```text
Use HCTI / HTML-CSS-to-Image for MVP.
Use Cloudinary for image storage and resizing.
```

---

## 13. Backend Language Decision

The backend can be built in either:

```text
FastAPI / Python
```

or

```text
Node.js / Express
```

Since this project includes AI agents, prompt workflows, content generation, and scheduling, the recommended backend is:

```text
FastAPI / Python
```

### Why FastAPI

- Good for AI workflows
- Good for background jobs
- Easy to integrate LLM APIs
- Clean API structure
- Fast development
- Suitable for content generation pipelines

### Final Recommendation

```text
Backend: FastAPI / Python
Mobile App: React Native Android
```

---

## 14. Recommended MVP Tech Stack

### Mobile App

```text
React Native + Expo
```

Purpose:

- Android admin app
- APK installation without Play Store
- View generated post
- Approve/reject/regenerate
- Edit caption
- View last 7 days backup

### Backend

```text
FastAPI / Python
```

Purpose:

- Generate posts
- Call NVIDIA API
- Call DeepSeek API
- Call image generation API
- Manage approval state
- Publish to Meta APIs

### LLM APIs

```text
NVIDIA API + DeepSeek API
```

Usage:

- NVIDIA for low-cost draft generation
- DeepSeek for educational accuracy and final review

### Image Generation

```text
HCTI / HTML-CSS-to-Image
```

Purpose:

- Generate branded social media images from templates

### Image Storage

```text
Cloudinary
```

Purpose:

- Store image for publishing
- Provide public image URL
- Resize/optimize images if needed

### Database

```text
Supabase PostgreSQL
```

Purpose:

- Store pending posts
- Store approval state
- Store 7-day backup
- Store publishing status

### Publishing

```text
Meta API
```

Purpose:

- Publish to Instagram
- Publish to Facebook Page

---

## 15. Meta API Readiness

Instagram publishing through Meta API requires:

- Instagram professional account, either Creator or Business
- Instagram account linked to a Facebook Page
- Facebook Page admin access
- Meta Developer account
- Meta app
- Required permissions
- Access tokens
- Possible Meta App Review

Meta App Review can take time, sometimes around 1–2 weeks depending on permissions, documentation quality, and review response.

Therefore, Meta setup should start on **Day 1**, not near the end of development.

### Meta Setup Checklist

1. Convert Instagram account to Creator or Business.
2. Link Instagram account to EduPlatform Facebook Page.
3. Confirm Facebook Page admin access.
4. Create Meta Developer account.
5. Create Meta App.
6. Add required products/permissions.
7. Prepare App Review if needed.
8. Generate test access token.
9. Test Facebook Page posting.
10. Test Instagram media publishing.

---

## 16. LLM Usage Plan

You already have:

- Free NVIDIA LLM API keys
- Paid DeepSeek API

### Suggested Usage

| Task | Recommended API |
|---|---|
| Topic idea generation | NVIDIA |
| First draft caption | NVIDIA |
| Hashtags | NVIDIA |
| Word of the Day | NVIDIA |
| Festival greeting draft | NVIDIA |
| Educational question generation | DeepSeek |
| Maths/science answer checking | DeepSeek |
| Final content quality check | DeepSeek |
| Suggestions for admin | DeepSeek or NVIDIA |

### Reason

Use NVIDIA for cheaper/general generation.

Use DeepSeek for:

- Accuracy
- Reasoning
- Educational questions
- Answer verification
- Final review

---

## 17. MVP Content Types

Start with only 5 content types.

### 1. Question of the Day

Used for:

- Maths
- Science
- English
- Social Science
- GK

Example:

```text
Question: Why do we see lightning before hearing thunder?
Answer: Because light travels faster than sound.
```

### 2. Word of the Day

Used for English vocabulary.

Example:

```text
Word: Curious
Meaning: Eager to know or learn something
Sentence: A curious student always asks questions.
```

### 3. Interesting Fact

Used for:

- Science facts
- History facts
- Geography facts
- GK facts

Example:

```text
Did you know?
The human body has 206 bones.
```

### 4. Festival Greeting

Used for local and national festivals.

Example:

```text
Edu Platform wishes you a Happy Diwali.
May this festival bring knowledge, discipline, and success.
```

### 5. Admission / Demo Class Post

Used for promotional posts.

Example:

```text
Admissions Open
Classes 6–12 | JEE | NEET | BPSC
Call: 1234567890 / 9643557068
```

---

## 18. Weekly Content Calendar

| Day | Post Type |
|---|---|
| Monday | Word of the Day |
| Tuesday | Maths Question |
| Wednesday | Science Fact / Science Question |
| Thursday | History / Geography / GK |
| Friday | English Grammar Tip |
| Saturday | Quiz / MCQ |
| Sunday | Motivation / Festival / Admission Post |

---

## 19. Required Templates

Create only 5 templates first.

### Template 1: Question of the Day

Fields:

```text
post_title
class_level
subject
question
answer
cta
phone
website
```

### Template 2: Word of the Day

Fields:

```text
word
meaning
sentence
cta
phone
website
```

### Template 3: Interesting Fact

Fields:

```text
fact_title
fact_text
subject
cta
phone
website
```

### Template 4: Festival Greeting

Fields:

```text
festival_name
greeting_message
brand_name
phone
website
```

### Template 5: Admission / Demo Class

Fields:

```text
headline
course_list
batch_info
cta
phone
address
website
```

---

## 20. Simplified Data Storage

You said the app does not need to store posts forever.

So the storage rule should be:

```text
Keep only 7 days of post backup after publishing.
```

### Keep for 7 Days

The system should keep:

- Image URL
- Caption
- Hashtags
- Suggestions
- Approval status
- Published status
- Error message if any
- Platform post IDs

### Delete After 7 Days

After 7 days, the system should delete:

- Generated image backup
- Caption backup
- Suggestions
- Old rejected/generated drafts

### Optional Minimal Log

Optional: keep a small publishing log for 30–90 days.

This log can store only:

```text
date
platform
success/failure
instagram_post_id
facebook_post_id
```

This is useful for debugging but not required.

---

## 21. Simplified Database Design

Only one main table is needed for MVP.

### Posts Table

```text
id
post_type
subject
class_level
topic
image_url
caption
hashtags
suggestions
fact_check_status
status
created_at
approved_at
published_at
instagram_post_id
facebook_post_id
error_message
expires_at
```

### Status Values

```text
generated
awaiting_approval
approved
published
rejected
failed
expired
```

### Expiry Rule

```text
expires_at = published_at + 7 days
```

A cleanup job should run daily and delete expired post backups.

---

## 22. Post Status Flow

```text
Generated
  ↓
Awaiting Approval
  ↓
Approved
  ↓
Published
  ↓
Backup Kept for 7 Days
  ↓
Deleted
```

Alternative flows:

```text
Awaiting Approval → Rejected → Deleted / Regenerate
Awaiting Approval → Edited → Approved → Published
Approved → Publishing Failed → Retry
```

---

## 23. Example Generated Post

### Post Type

```text
Question of the Day
```

### Subject

```text
Class 8 Science
```

### Question

```text
Why do we see lightning before hearing thunder?
```

### Answer

```text
Because light travels faster than sound.
```

### Caption

```text
Question of the Day from Edu Platform.

We see lightning before hearing thunder because light travels faster than sound.

Keep learning with EduPlatform.

Admissions open for Classes 6–12, JEE, NEET and BPSC preparation.

Call: 1234567890 / 9643557068
```

### Hashtags

```text
#EduPlatformTheFoundation #EduPlatformCoaching #Class8Science #ScienceFacts #CBSE #BSEB #DailyLearning
```

---

## 24. MVP Safety Rules

### Educational Safety

The system should:

- Verify every educational answer.
- Avoid fake facts.
- Avoid controversial claims.
- Avoid complex language for younger classes.
- Give short and simple explanations.

### Brand Safety

The system should not post:

- Political opinions
- Religious comparisons
- Offensive jokes
- Unverified results
- Misleading admission claims
- Sensitive or controversial content

### Promotional Balance

Recommended ratio:

```text
70% educational content
20% engagement content
10% promotional content
```

---

## 25. Error Handling

### Image Generation Failed

Action:

```text
Show error → Allow regenerate
```

### LLM Content Failed

Action:

```text
Retry with simpler prompt → Show fallback draft
```

### Meta Posting Failed

Action:

```text
Save as failed → Show retry button
```

### Access Token Expired

Action:

```text
Show reconnect Meta account message
```

### Admin Did Not Approve

Action:

```text
Keep post in Awaiting Approval for a limited time
```

---

## 26. Updated MVP Development Timeline

### Week 1: Setup and Decisions

Tasks:

- Confirm Instagram is Creator or Business account.
- Link Instagram to EduPlatform Facebook Page.
- Confirm Facebook Page admin access.
- Create Meta Developer account.
- Create Meta app.
- Start Meta API permission and App Review preparation on Day 1.
- Finalize React Native Android app as the main phone app approach.
- Decide Expo or React Native CLI.
- Decide HCTI / HTML-CSS-to-Image for image generation.
- Collect logo and brand colors.
- Finalize 5 templates.
- Finalize FastAPI + React Native stack.

### Week 2: Content Engine

Tasks:

- Connect NVIDIA API.
- Connect DeepSeek API.
- Build post generation flow.
- Build fact-checking flow.
- Add prompt templates.
- Add weekly content rotation.

### Week 3: Image Engine

Tasks:

- Create 5 HTML/CSS templates.
- Connect HCTI / HTML-CSS-to-Image.
- Connect Cloudinary.
- Generate preview images.
- Test text length handling.

### Week 4: React Native Admin App

Tasks:

- Build mobile login.
- Build today’s post screen.
- Add image preview.
- Add caption edit.
- Add approve/reject/regenerate buttons.
- Add last 7 days backup screen.
- Generate first test APK.

### Week 5: Meta Publishing

Tasks:

- Connect Facebook Page API.
- Connect Instagram publishing API.
- Add approved-post publishing.
- Store platform post IDs.
- Add failed-post retry.
- Add token expiry handling.

### Week 6: Testing and Launch

Tasks:

- Test 20–30 generated posts.
- Test image formatting on phone.
- Test approval flow.
- Test publishing flow.
- Test 7-day cleanup.
- Generate final MVP APK.
- Install APK on admin phone.
- Start daily approval-based posting.

---

## 27. Cost Areas

### Free / Low-Cost

Possible free or low-cost parts:

- NVIDIA free LLM credits
- Cloudinary free tier
- Supabase free tier
- Render/Railway starter hosting
- HCTI / HTML-CSS image API testing tier
- React Native development
- APK sideloading without Play Store

### Paid

Likely paid parts:

- DeepSeek usage
- Developer cost
- Hosting after free tier
- Image generation API after free limit
- Domain/server if needed

### Meta Cost

Meta usually does not charge directly per basic API post, but the system must follow Meta developer rules and permission requirements.

### Play Store Cost

No Play Store upload is needed for this MVP.

---

## 28. Final MVP Deliverable

The final MVP should allow the admin to do this on phone:

```text
Open EduPlatform React Native admin app
↓
See today’s AI-generated post
↓
Review image, caption, hashtags, and suggestions
↓
Edit caption if needed
↓
Click Approve
↓
System posts to Instagram and Facebook
↓
System keeps backup for 7 days
```

The deliverable should include:

- Android APK file
- Backend API
- Database setup
- Image generation templates
- Meta publishing setup
- Basic documentation for installing APK manually

---

## 29. APK Update Process

Since there is no Play Store:

```text
Developer builds new APK
↓
Admin downloads new APK
↓
Admin installs it over old version
↓
App gets updated
```

Important:

- Keep app package name same for updates.
- Keep signing key safe.
- If signing key changes, Android may not update the old app and may require uninstalling first.
- Manual APK update is acceptable for personal/internal app.

---

## 30. Success Criteria

The MVP is successful if:

1. It generates one good post per day.
2. Admin can use the React Native app easily on phone.
3. No Play Store upload is required.
4. APK can be installed directly on Android.
5. Image design is consistent with EduPlatform branding.
6. Educational answers are correct.
7. Admin can approve, reject, regenerate, and edit.
8. Approved posts publish successfully.
9. Only 7 days of backup are kept.
10. Meta setup starts from Day 1.
11. The system reduces manual social media work.

---

## 31. Future Additions After MVP

After MVP, add:

1. Weekly content calendar approval
2. Auto scheduling
3. Festival calendar integration
4. Reels script generation
5. Student comment reply suggestions
6. WhatsApp enquiry follow-up
7. Basic analytics dashboard
8. Lead capture form
9. Parent enquiry automation
10. Push notifications
11. Optional Play Store release later
12. Optional iOS version later

---

## 32. One-Line Summary

EduPlatform should first build a simple React Native Android admin app where AI generates daily posts, creates branded images using HTML/CSS templates, shows suggestions to admin, publishes approved posts to Instagram and Facebook through Meta APIs, and keeps only 7 days of backup.
