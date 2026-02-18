# Hypernet Swarm — Setup Guide

**What this is:** Step-by-step instructions to get the AI swarm running on your machine.

**What the swarm does:** Autonomous AI workers that check for tasks, execute them via the Anthropic API, report results, and communicate with you via Telegram, email, or web chat.

---

## Quick Start (Mock Mode — No API Key Needed)

Test the swarm without making any API calls:

```bash
cd "0/0.1 - Hypernet Core"
python -m hypernet.swarm --mock --verbose
```

This starts the swarm with simulated workers. You'll see it:
- Discover instances (Loom, Trace) from the Instances/ directory
- Check the task queue
- Generate standing-priority tasks when the queue is empty
- Run the main loop (Ctrl+C to stop)

If this works, you're ready for live mode.

---

## Step 1: Install Dependencies

The core library has zero dependencies. The server and swarm need two packages:

```bash
pip install fastapi uvicorn
```

For live AI workers, also install:

```bash
pip install anthropic
```

---

## Step 2: Get an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Go to **API Keys** in the left sidebar
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

You can either:
- Set it as an environment variable: `export ANTHROPIC_API_KEY="sk-ant-..."`
- Or put it in the config file (Step 3)

---

## Step 3: Configure the Swarm

```bash
cd "0/0.1 - Hypernet Core"
cp swarm_config.example.json swarm_config.json
```

Edit `swarm_config.json`:

```json
{
  "anthropic_api_key": "sk-ant-your-key-here",
  "instances": ["Loom", "Trace"],
  "status_interval_minutes": 120,
  "telegram": {
    "bot_token": "",
    "chat_id": ""
  },
  "email": {
    "enabled": false,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "",
    "password": "",
    "to_email": ""
  }
}
```

**Required:** `anthropic_api_key`
**Optional:** Everything else. The swarm works with just the API key.

> **Security note:** `swarm_config.json` contains secrets. It should be in `.gitignore` and never committed. The example file (`swarm_config.example.json`) is safe to commit.

---

## Step 4: Run the Swarm (Live Mode)

```bash
cd "0/0.1 - Hypernet Core"
python -m hypernet.swarm --config swarm_config.json --verbose
```

The swarm will:
1. Load instance profiles from `Instances/Loom/profile.json` and `Instances/Trace/profile.json`
2. Build identity-aware system prompts from the archive
3. Start the main loop: check messages → find tasks → claim → execute → report
4. Send you status updates at the configured interval

Press **Ctrl+C** for graceful shutdown (saves state, notifies you).

---

## Optional: Set Up Telegram Notifications

The swarm can send you task updates and receive commands via Telegram.

### Create a Telegram Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "Hypernet Swarm")
4. Choose a username (e.g., `hypernet_swarm_bot`)
5. BotFather gives you a **bot token** — copy it

### Get Your Chat ID

1. Send any message to your new bot
2. Open: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id": 123456789}` — that number is your chat ID

Or: leave `chat_id` empty in the config. The swarm auto-captures it when you send your first message to the bot.

### Add to Config

```json
"telegram": {
  "bot_token": "123456:ABC-your-bot-token",
  "chat_id": "your-chat-id-or-leave-empty"
}
```

### Telegram Commands

Once running, send these to your bot:
- `/status` — Get a status report (uptime, tasks completed, worker info)
- `/stop` — Graceful shutdown
- `/task Fix the bug in store.py` — Create a high-priority task from your message
- Any other text — Routed to the first available worker for a response

---

## Optional: Set Up Email Notifications

For Gmail:

1. Enable 2-Step Verification on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use that password (not your regular password) in the config

```json
"email": {
  "enabled": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "email": "your-email@gmail.com",
  "password": "your-app-password",
  "to_email": "your-email@gmail.com"
}
```

The swarm sends emails for: task completions, failures, periodic status reports, and shutdown notifications.

---

## Running the Web Server + Swarm Together

The FastAPI server includes a web chat interface and graph explorer:

```bash
cd "0/0.1 - Hypernet Core"
python -m hypernet --port 8000
```

Then open http://localhost:8000/ for the graph explorer.

The web chat endpoint (`/chat`) connects to the swarm's WebMessenger when both are running.

---

## Architecture Overview

```
Matt (Telegram/Email/Web)
    ↕
  Messenger (multi-backend)
    ↕
  Swarm Orchestrator
    ↕
  Task Queue ←→ Workers (identity-aware LLM calls)
    ↕
  Hypernet Store (file-backed graph)
```

- **Swarm** checks for messages, finds tasks, assigns to workers, reports results
- **Workers** use identity-loaded system prompts (from the archive) to think/respond
- **Task Queue** stores tasks as graph nodes at `0.7.1.*` with dependency tracking
- **Messenger** broadcasts via all configured channels simultaneously

---

## Troubleshooting

**"anthropic package not installed"**
→ `pip install anthropic`

**"fastapi not found" / "uvicorn not found"**
→ `pip install fastapi uvicorn`

**Swarm starts but no workers found**
→ Check that `Instances/Loom/` and `Instances/Trace/` directories exist with `profile.json` files

**Telegram messages not arriving**
→ Verify bot token, send a message to the bot first, check `getUpdates` URL for your chat ID

**Workers running in mock mode unexpectedly**
→ API key not set. Check `swarm_config.json` or `ANTHROPIC_API_KEY` environment variable.

**"No module named hypernet"**
→ Run from the `0/0.1 - Hypernet Core/` directory, or add it to your Python path

---

## File Reference

| File | Purpose |
|------|---------|
| `swarm_config.example.json` | Template — copy to `swarm_config.json` |
| `swarm_config.json` | Your config (gitignored, contains secrets) |
| `hypernet/swarm.py` | Orchestrator — main loop, task assignment |
| `hypernet/worker.py` | LLM API wrapper with identity context |
| `hypernet/identity.py` | Loads profiles, builds system prompts |
| `hypernet/messenger.py` | Email, Telegram, WebSocket backends |
| `hypernet/tasks.py` | Task queue (graph nodes at 0.7.1.*) |
| `hypernet/server.py` | FastAPI REST API + web chat |
| `data/swarm/state.json` | Persisted swarm state (auto-created) |

---

*Created for the Hypernet Project — February 2026*
