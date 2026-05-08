# 🤖 Auto Bidding Bot — LinkedIn

An automated system that detects posts where users are looking for
freelancers/developers on LinkedIn and automatically posts a
personalized AI-generated bid comment.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **n8n** | Workflow orchestration and scheduling |
| **Python + Playwright** | Browser automation |
| **FastAPI** | Backend API server |
| **Groq AI** | AI comment generation |
| **Google Sheets** | Deduplication storage |

---

## 🏗️ Architecture

```
n8n Schedule Trigger (every 3 hours)
        ↓
FastAPI /search-posts
→ Playwright searches LinkedIn
→ Returns post content + ID
        ↓
n8n checks Google Sheets
→ Duplicate? → Skip
→ New post?  → Continue
        ↓
n8n sends post to Groq AI
→ Generates personalized comment
        ↓
FastAPI /post-comment
→ Playwright opens post
→ Types and submits comment
        ↓
n8n saves post ID to Google Sheets
```

---

## 📁 Project Structure

```
auto-bidding-bot/
├── main.py              # FastAPI server (two endpoints)
├── linkedin_bot.py      # Playwright browser automation
├── login.py             # One time LinkedIn session setup
├── requirements.txt     # Python dependencies
├── .gitignore           # Ignored files
└── README.md            # Project documentation

```

---

## ⚙️ Setup Instructions

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/auto-bidding-bot
cd auto-bidding-bot
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 3 — LinkedIn Login (One Time Only)

```bash
python login.py
```

A browser window will open. Login to LinkedIn manually
then press Enter in the terminal. Your session will be
saved in the `session/` folder for all future runs.

### Step 4 — Start FastAPI Server

```bash
uvicorn main:app --reload --port 8000
```

Keep this terminal open while the bot is running.

### Step 5 — Configure n8n Workflow

Set up the following in n8n:
- Google Sheets credentials
- Groq API key
- Schedule timing (every 3 hours)
- Business hours filter (9AM - 6PM)

---

## 🔌 API Endpoints

### GET `/search-posts`

Playwright searches LinkedIn for relevant developer posts.

**Response:**
```json
{
  "posts": [
    {
      "post_id": "7458413120911462400",
      "post_url": "https://linkedin.com/feed/update/urn:li:activity:...",
      "post_content": "We are looking for a .NET developer..."
    }
  ]
}
```

---

### POST `/post-comment`

Playwright opens the post and submits the AI-generated comment.

**Request Body:**
```json
{
  "post_url": "https://linkedin.com/feed/update/urn:li:activity:...",
  "comment": "I am excited to apply for this opportunity..."
}
```

**Response:**
```json
{
  "status": "success",
  "post_url": "https://linkedin.com/feed/update/urn:li:activity:..."
}
```

---

## 🔄 n8n Workflow Nodes

```
1. Schedule Trigger     → Runs every 3 hours (9AM - 6PM)
2. HTTP Request         → GET /search-posts
3. Google Sheets        → Check if post_id already exists
4. IF Node              → Duplicate? Stop : Continue
5. AI Agent (Groq)      → Generate personalized comment
6. Wait Node            → 15 second delay
7. HTTP Request         → POST /post-comment
8. Google Sheets        → Save post_id + timestamp
```

---

## 🗄️ Google Sheets Schema

| post_id | post_url | post_content | platform | comment | timestamp |
|---|---|---|---|---|---|
| 7458413120911462400 |https://www.linkedin.com/feed/update/urn:li:activity:7458114866596474369 | We are expanding our team... | linkedin | I'm excited to join... | 2026-05-08 10:30:00 |
| 7458107006780915714 | https://www.linkedin.com/feed/update/urn:li:activity:745811486568968425 | We are looking for frontend...|linkedin | I have a skills that... | 2026-05-08 13:45:00 |

---

## 🛡️ Safety & Anti-Detection Measures

| Measure | Detail |
|---|---|
| **Daily limit** | 1 post per run, max 10-15/day |
| **Human delays** | Random 2-5 second waits between actions |
| **Business hours** | Only runs 9AM - 6PM |
| **Persistent session** | Reuses saved login cookies |
| **Deduplication** | Never comments on same post twice |
| **Character typing** | Types one character at a time |

---

## 🤖 AI Comment Generation

Groq AI generates personalized comments based on post content.

**Example Input to Groq:**
```
Post: "We are looking for a .NET developer to join our team."
```

**Example Output from Groq:**
```
I am excited about the opportunity to join your team as a
.NET developer and contribute my skills and experience to
help drive your projects forward. I'd love to discuss my
qualifications further and explore how I can make a
meaningful impact as part of your team.
```

---

## ⚠️ Important Notes

- Never use your **personal** LinkedIn account
- Always use a **fresh dedicated** account
- `session/` folder is gitignored for security
- `.env` file is gitignored to protect API keys
- Screenshots are gitignored for privacy

---

## 📦 Requirements

```
fastapi
uvicorn
playwright
python-dotenv
requests
```

---

## 🚀 Running Order

```bash
# Step 1 — First time only
python login.py

# Step 2 — Every time you start
uvicorn main:app --reload --port 8000

# Step 3 — Activate n8n workflow
# Open http://localhost:5678 and activate
```

---

## 👩‍💻 Author

Uzma Khatun

📧 uzmakhatun0205@gmail.com  
🔗 [GitHub](https://github.com/UzmaKhatun)
🔗 [LinkedIn](https://www.linkedin.com/in/uzma-khatun-88b990334/)
🔗 [Portfolio](https://portfolio-uzmakhatun.netlify.app/)

---

Made with 💖
