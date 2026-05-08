# ⚡ DevSync

> **An AI-powered terminal agent that monitors your local processes, intercepts input prompts, reasons about them using your project context, and lets you respond from your phone — keeping your jobs running while you're away.**

```
Process stdout → Classifier → Reasoning Engine → Telegram alert → You tap → Process resumes
```

---

## The Problem

You kick off a long job — ML training, Docker build, database migration, package install. It runs for 20–40 minutes. You step away.

You come back to find the process frozen at:

```
Overwrite existing config? [Y/n]:
```

It's been waiting 45 minutes. Your GPU was idle. Your time was wasted.

**Existing workarounds don't cut it:**

| Tool | Why it fails |
|---|---|
| `tmux` / `screen` | Still requires you to physically go back and respond |
| `yes \|` | Blindly answers Y to everything — dangerous |
| SSH keep-alive | Prevents disconnection only, no automated response |
| Stay at your desk | Kills your productivity |

None of these are intelligent. None understand your project context. None work from your phone.

---

## The Solution

DevSync wraps any process and watches its stdout in real time. When it detects a prompt, it:

1. **Classifies** the event (input required, error, milestone, or noise)
2. **Reasons** about it using your project's `SOUL.md` rules via Groq (llama-3.3-70b)
3. **Alerts** you on Telegram with the AI's recommendation and context
4. **Injects** your response (Y / N / Custom) back into the process stdin

It doesn't just forward your terminal to your phone. It thinks before it notifies you.

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│              DEVELOPER'S LOCAL MACHINE          │
│                                                 │
│  ┌─────────────┐                                │
│  │ Any Process │  (train.py, pip, docker, etc.) │
│  └──────┬──────┘                                │
│         │ stdout                                │
│         ▼                                       │
│  ┌──────────────────────────────────┐           │
│  │   wrapper.py  (Python + PTY)     │           │
│  │   ┌──────────────────────────┐   │           │
│  │   │  classifier.py           │   │           │
│  │   │  regex + LLM fallback    │   │           │
│  │   └──────────┬───────────────┘   │           │
│  │              │                   │           │
│  │   ┌──────────▼───────────────┐   │           │
│  │   │  reasoning/engine.py     │   │           │
│  │   │  Groq API + SOUL.md      │   │           │
│  │   └──────────┬───────────────┘   │           │
│  └──────────────┼───────────────────┘           │
│                 │ WebSocket event               │
│                 ▼                               │
│  ┌──────────────────────────────────┐           │
│  │   gateway/server.js (Node.js)    │           │
│  │   gateway/bot.js  (Telegram Bot) │           │
│  └──────────────┬───────────────────┘           │
└─────────────────┼───────────────────────────────┘
                  │
                  ▼
        📱 Telegram alert on your phone
                  │
                  │ tap Y / N / Custom
                  ▼
        stdin injected → process resumes
```

---

## Demo Scenarios

**Scene 1 — Checkpoint overwrite**

Training hits `Checkpoint exists at /runs/exp_041. Overwrite? [Y/n]:` — DevSync detects it, reasons against `SOUL.md`, recommends Y (safe, failed run), pushes to Telegram. You tap Yes. Training continues.

**Scene 2 — HIGH RISK danger block**

Script hits `WARNING: This will DROP TABLE users. Confirm? [Y/n]:` — DevSync catches the `DROP` keyword. No AI suggestion. No auto-approve. Alert shows `🚨 HIGH RISK DETECTED — Manual response required`. You must tap manually.

---

## Project Memory — `SOUL.md`

DevSync reads `SOUL.md` at the repo root before every AI recommendation. Edit it to define project-specific rules:

```markdown
# Project: MyApp

## Stack
Django, Celery, Redis, PostgreSQL, Docker

## Safe Defaults
- pip installs: Y unless version conflict detected
- overwrite checkpoints: Y if on experiment branch
- overwrite migrations: NEVER
- database drops: NEVER auto-approve

## Alert Always
- Any prompt containing "DROP"
- Any prompt containing "purge"
- Any authentication prompt
```

The reasoning engine reads this before every recommendation — so suggestions are project-aware, not generic.

---

## Architecture

| Module | Stack | Role |
|---|---|---|
| `wrapper.py` | Python, `pty`, `psutil` | Spawns process, reads stdout, injects stdin |
| `classifier.py` | Python, regex, Groq | Detects prompt type: INPUT_REQUIRED / ERROR / MILESTONE / NOISE |
| `reasoning/engine.py` | Python, Groq (llama-3.3-70b) | Reads SOUL.md, recommends Y/N with reason |
| `gateway/server.js` | Node.js, WebSocket | Routes events between Python wrapper and Telegram bot |
| `gateway/bot.js` | Telegram Bot API | Sends alerts, receives taps, formats messages |
| `SOUL.md` | Markdown | Project-specific memory and rules |

### Data Contracts

- **Contract A** — Raw terminal lines + metadata (Wrapper → Classifier)
- **Contract B** — Classified event type + extracted prompt (Classifier → Engine)
- **Contract C** — AI recommendation + reasoning (Engine → Gateway)
- **Contract D** — User response + operational mode (Gateway → Wrapper → stdin)

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/downloads)
- A Telegram bot token — create via [@BotFather](https://t.me/BotFather)
- Your Telegram chat ID — get via [@userinfobot](https://t.me/userinfobot)
- A Groq API key — get at [console.groq.com](https://console.groq.com)

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/gsvenkatsai/DevSync.git
cd DevSync
git checkout dev
```

**2. Configure environment**

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
GROQ_API_KEY=your_groq_api_key_here
```

**3. Run**

```bash
docker-compose up --build
```

**4. Stop**

```bash
docker-compose down
```

---

## Usage

**Wrap any process:**

```bash
devsync run python train.py --epochs 50
devsync run pip install -r requirements.txt
devsync run docker-compose up --build
devsync run alembic upgrade head
```

DevSync wraps the process and begins monitoring stdout. Walk away. You'll get a Telegram alert if anything needs your attention.

**Telegram response buttons:**

| Button | Action |
|---|---|
| ✅ Yes | Injects `Y\n` into stdin |
| ❌ No | Injects `N\n` into stdin |
| ✏️ Custom | Prompts you to type a custom response |
| 🔒 Auto / Safe Defaults | Resolves based on SOUL.md rules automatically |

**Session summary on completion:**

```
✅ DevSync — Job Complete
━━━━━━━━━━━━━━━
📋 train.py finished in 2h 14m
🔔 Prompts: 2 resolved (1 auto, 1 manual)
⚠️  Warnings: 1 (non-fatal)
📁 Log: ~/.devsync/sessions/042.log
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Process management | Python `subprocess` + `pty` / `pywinpty` |
| Prompt classification | Regex + Groq LLM fallback |
| Reasoning engine | Groq API (`llama-3.3-70b`) |
| Project memory | `SOUL.md` |
| Gateway | Node.js + WebSocket (`ws`) |
| Notification | Telegram Bot API |
| Process health | `psutil` |
| Container | Docker + Docker Compose |

---

## KPIs

| Metric | Target |
|---|---|
| Prompt detection latency | < 3 seconds from pause to Telegram alert |
| Prompt detection accuracy | > 90% on known prompt patterns |
| False positive rate | < 1 noise notification per 10-minute run |
| End-to-end response injection | < 5 seconds from tap to process resume |
| Process resume success rate | 100% on test cases |

---

## Classifier — Supported Prompt Patterns

Layer 1 regex covers:

```
[Y/n]  [y/N]  yes/no  password:  continue?  Proceed?
Overwrite  already exists  Press any key  Are you sure  (y/n)
```

Layer 2 LLM fallback fires if the process goes silent for 10+ seconds with no regex match — asks Groq: *"Is this output waiting for user input?"*

---
