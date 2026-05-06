# DevSync

An AI-powered terminal agent that monitors your local processes, intercepts input prompts, reasons about them using your project context, and lets you respond from your phone — keeping your jobs running while you're away.

## How It Works

```
Process stdout → Classifier → Reasoning Engine → Telegram alert → You tap → Process resumes
```

1. You run a long process (ML training, Docker build, migrations, etc.)
2. DevSync wraps it and monitors stdout
3. When a prompt is detected, it sends a Telegram alert with an AI recommendation
4. You tap Y / N / Custom from your phone
5. DevSync injects the response and the process continues

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/downloads)
- A Telegram bot token — create one via [@BotFather](https://t.me/BotFather)
- Your Telegram chat ID — get it via [@userinfobot](https://t.me/userinfobot)
- A Groq API key — get one at [console.groq.com](https://console.groq.com)

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/gsvenkatsai/DevSync.git
cd DevSync
git checkout dev
```

**2. Create your `.env` file**

Copy the example file and rename it:

```bash
cp .env.example .env
```

Open `.env` in any text editor and fill in your credentials:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
GROQ_API_KEY=your_groq_api_key_here
```

**3. Run**

```bash
docker-compose up --build
```

---

## Demo

The default setup runs a simulated ML training script (`test_script.py`) that demonstrates two scenarios:

**Scene 1 — Checkpoint overwrite**

- A fake training run hits: `Checkpoint exists at /runs/exp_041. Overwrite? [Y/n]:`
- DevSync detects the prompt, reasons using `SOUL.md` project rules
- Telegram alert arrives with AI recommendation and Y/N/Custom/Auto buttons
- Tap Y → process resumes

**Scene 2 — HIGH RISK danger block**

- Script hits: `WARNING: This will DROP TABLE users. Confirm? [Y/n]:`
- DevSync detects the danger word `DROP` — no AI suggestion, auto-approve blocked
- Telegram alert shows `🚨 HIGH RISK DETECTED — Manual response required`
- You must manually tap to respond

---

## Project Memory (SOUL.md)

DevSync reads `SOUL.md` at the repo root before every AI recommendation. Edit it to add your project-specific rules:

```markdown
# Project: MyApp

## Safe Defaults

- overwrite checkpoints: Y if on experiment branch
- pip installs: Y unless version conflict

## Alert Always

- Any prompt containing "DROP"
- Any prompt containing "purge"
- Any authentication prompt
```

---

## Architecture

```
wrapper.py   →   classifier.py   →   engine.py   →   server.js   →   Telegram
   ↑                                                      |
   └──────────────── Contract D (stdin inject) ───────────┘
```

| Module           | Stack                                | Role                                                 |
| ---------------- | ------------------------------------ | ---------------------------------------------------- |
| Wrapper          | Python, pty, psutil                  | Spawns process, reads stdout, injects stdin          |
| Classifier       | Python, regex, Groq                  | Detects prompt type (INPUT_REQUIRED / ERROR / NOISE) |
| Reasoning Engine | Python, Groq (llama-3.3-70b)         | Reads SOUL.md, recommends Y/N with reason            |
| Gateway + Bot    | Node.js, Telegram Bot API, WebSocket | Routes alerts to phone, returns response             |

---

## Stack

- Python 3.11, Groq API (llama-3.3-70b), websocket-client, psutil
- Node.js 18, Telegram Bot API, WebSocket (ws)
- Docker + Docker Compose

---

## Stopping DevSync

```bash
docker-compose down
```
