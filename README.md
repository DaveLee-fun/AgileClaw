<div align="center">

# 🦅 AgileClaw

### *The AI agent that measures → learns → improves on its own*

> ⚠️ **Work in Progress** — actively developed. APIs and config format may change.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://anthropic.com)
[![Telegram](https://img.shields.io/badge/channel-Telegram-blue.svg)](https://telegram.org)
[![Status](https://img.shields.io/badge/status-WIP-red.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**A lightweight personal AI agent with a built-in agile loop.**  
Full PC access · Claude-powered · Telegram native · Cron scheduler  
*Built for solo entrepreneurs, indie hackers, and small teams.*

[Quick Start](#-quick-start) · [How It Works](#-how-the-agile-loop-works) · [Architecture](#-architecture) · [vs OpenClaw/nanoclaw](#-why-agileclaw)

</div>

---

## What is AgileClaw?

AgileClaw is a **personal AI agent** that lives on your machine and runs a continuous agile loop:

> **Set goals → Measure KPIs → Analyze results → Improve automatically → Repeat**

It's not just another chatbot. AgileClaw **knows your goals**, **checks your metrics**, and **suggests concrete next steps** — every day, automatically.

**Inspired by [OpenClaw](https://github.com/openclaw/openclaw) and [nanoclaw](https://github.com/qwibitai/nanoclaw)** — full PC access, no sandboxing. AgileClaw adds the missing piece: **a structured agile feedback loop so the agent actually improves your results over time.**

**Who it's for:**
- 🧑‍💻 **Solo entrepreneurs** who want an AI that tracks their business KPIs
- 🚀 **Indie hackers** running multiple projects without a team
- 👥 **Small teams** who want agile rituals without the overhead

---

## Why AgileClaw?

There are three tiers of AI agent tools:

**🏢 Full platforms** (OpenClaw, nanoclaw) — powerful, but broad-purpose and complex to self-host  
**🔬 Research frameworks** (AutoGen, CrewAI, LangChain) — built for multi-agent research, not daily personal use  
**🦅 AgileClaw** — the missing middle: opinionated, goal-driven, simple enough to read in an afternoon

| Feature | AgileClaw | OpenClaw | nanoclaw | AutoGen | LangChain |
|---------|:---------:|:--------:|:--------:|:-------:|:---------:|
| Built-in agile loop | ✅ | ❌ | ❌ | ❌ | ❌ |
| Full PC access (no sandbox) | ✅ | ✅ | ✅ | ✅ | ❌ |
| KPI-driven goals | ✅ | ❌ | ❌ | ❌ | ❌ |
| < 500 lines of core code | ✅ | ❌ | ✅ | ❌ | ❌ |
| Telegram native | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cron scheduler built-in | ✅ | ✅ | ❌ | ❌ | ❌ |
| File-based memory (no DB) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Self-hostable on your laptop | ✅ | ✅ | ✅ | ✅ | ✅ |
| Subscription / cloud required | ❌ | ❌ | ❌ | ❌ | ❌ |

**AgileClaw vs OpenClaw:** OpenClaw is a full-featured platform with GUI, extensions, and marketplace. AgileClaw is a tiny hackable core you can read, fork, and own completely.

**AgileClaw vs nanoclaw:** nanoclaw is a minimal agent scaffold. AgileClaw keeps the same simplicity but adds the agile loop, cron scheduling, and KPI tracking on top.

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/DaveLee-fun/AgileClaw.git
cd AgileClaw
./setup.sh
```

### 2. Configure

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
```

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"       # Get from @BotFather
  allowed_users: [YOUR_USER_ID]     # Your Telegram user ID

claude:
  api_key: "YOUR_CLAUDE_API_KEY"    # From console.anthropic.com
  model: "claude-sonnet-4-5"

memory:
  dir: "./memory"

cron:
  jobs_file: "./cron_jobs.json"
```

### 3. Set Your Goals

Edit `memory/goals.md`:

```markdown
# My Goals

## KPIs
| Metric          | Current | Target |
|-----------------|---------|--------|
| MRR             | $500    | $2,000 |
| Newsletter subs | 320     | 1,000  |
| Daily users     | 150     | 500    |

## How to Measure
- MRR: check Stripe dashboard (run script scripts/stripe_mrr.py)
- Newsletter: curl https://api.myplatform.com/subscribers
- Daily users: check analytics API
```

### 4. Run

```bash
python main.py
```

Then in Telegram: `/agile` → get your daily KPI report + action items.

---

## 🔄 How the Agile Loop Works

```
┌─────────────────────────────────────────────────────────┐
│                    AGILE LOOP                           │
│                                                         │
│   📋 GOALS          🔍 MEASURE         📊 ANALYZE       │
│   goals.md    →    use tools     →    compare vs       │
│   KPI targets      shell/web/api      targets           │
│       │                                    │            │
│       └────────────────────────────────────┘            │
│                         ↓                               │
│   🚀 IMPROVE         ✅ REPORT                          │
│   suggest top 3  ←   what's working /                  │
│   next actions       what's not                         │
└─────────────────────────────────────────────────────────┘
```

**Runs automatically** via cron (e.g., every morning at 9am):
```json
{
  "name": "daily-agile",
  "schedule": "0 9 * * *",
  "task": "Run agile review and send results to Telegram"
}
```

---

## 🏗 Architecture

```
agileclaw/
├── main.py              # Entry point (< 80 lines)
├── config.example.yaml  # Config template
├── core/
│   ├── agent.py         # Main agent loop + tool orchestration
│   ├── claude.py        # Claude API client (tool_use loop)
│   └── memory.py        # File-based memory (no DB needed)
├── channels/
│   └── telegram.py      # Telegram bot integration
├── tools/
│   ├── shell.py         # Run shell commands
│   ├── files.py         # Read/write files
│   ├── web.py           # Fetch web pages
│   └── browser.py       # Browser control (Playwright)
├── scheduler/
│   └── cron.py          # Cron job scheduler (APScheduler)
└── agile/
    ├── loop.py          # Agile review logic + prompts
    └── goals.md         # Your goals template
```

**Core code is tiny:** `core/` + `agile/` is under 300 lines total. Read it in 15 minutes.

---

## 🛠 Tools Available

| Tool | What It Does |
|------|-------------|
| `shell` | Run any shell command (scripts, CLIs, APIs) |
| `read_file` | Read any file on your machine |
| `write_file` | Write/update any file |
| `web_fetch` | Fetch a URL, extract readable content |
| `browser_open` | Open a URL in Playwright browser |
| `browser_click` | Click a page element |
| `browser_type` | Type into an input field |
| `browser_get_text` | Extract text from current page |
| `browser_screenshot` | Take a screenshot |

---

## 💡 Use Cases

**📱 App maker tracking installs**
> "Check my App Store stats, compare vs last week, tell me what to do next"

**📝 Content creator tracking engagement**
> "Measure my Threads/Reddit engagement today vs my weekly target"

**💰 SaaS founder tracking MRR**
> "Pull Stripe MRR, check churn vs target, suggest top priority"

**📚 Course creator tracking students**
> "Check new enrollments this week, compare vs goal, what should I post today?"

---

## 🗺 Roadmap

- [x] Core agent loop (Claude + tools)
- [x] Telegram channel
- [x] Cron scheduler
- [x] Agile review loop
- [x] File-based memory
- [ ] Discord channel support
- [ ] Web dashboard for KPI visualization
- [ ] Plugin/skill system for custom tools
- [ ] Pre-built skill packs (App Store, Stripe, Reddit, Threads)
- [ ] Multi-agent support (delegate tasks to sub-agents)

---

## 🤝 Contributing

AgileClaw is intentionally small. Before adding features, ask:
> *"Can this be done in a shell script or custom skill instead?"*

1. Fork it
2. Make your change (keep it small)
3. Open a PR

**Great first contributions:**
- New tool (e.g., `tools/slack.py`, `tools/notion.py`)
- New channel (e.g., `channels/discord.py`)
- Example skill in `skills/`
- Bug fixes

---

## 📜 License

MIT — do whatever you want with it.

---

<div align="center">

*Built on the shoulders of [OpenClaw](https://github.com/openclaw/openclaw) and [nanoclaw](https://github.com/qwibitai/nanoclaw).*  
*If you find this useful, consider starring ⭐ the repo.*

</div>
