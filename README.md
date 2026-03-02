<div align="center">

# 🦅 AgileClaw

### *The AI agent that measures → learns → improves on its own*

> 🚧 **Early Stage — Not Yet Functional**
>
> This project is in its **initial development phase**. The code is being actively built and is **not ready to run yet**.
> APIs, config format, and structure will change significantly.
> Watch/Star to follow progress — contributions and ideas welcome!

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://anthropic.com)
[![Telegram](https://img.shields.io/badge/channel-Telegram-blue.svg)](https://telegram.org)
[![Status](https://img.shields.io/badge/status-WIP-red.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**A lightweight personal AI agent with a built-in agile loop.**
Full PC access · Claude-powered · Telegram native · Cron scheduler
*Built for solo entrepreneurs, indie hackers, and small teams.*

[Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Architecture](#-architecture) · [Why AgileClaw](#-why-agileclaw)

</div>

---

## What is AgileClaw?

AgileClaw is a **personal AI agent** that treats every goal as an independent **Agile Team** — with its own charter, KPIs, and execution loop.

> **Set a goal → Auto-create a team → Measure KPIs → Analyze → Improve → Repeat**

It's not just another chatbot. When you say *"grow my Twitter followers to 5,000"*, AgileClaw automatically:
1. Creates a dedicated **Agile Team** for that goal with a charter file
2. Defines *how* each KPI will be measured (API, script, or manual)
3. Executes tasks using tools (shell, web, browser)
4. Runs scheduled reviews: daily reports, weekly retrospectives

Inspired by **[OpenClaw](https://github.com/openclaw/openclaw)** and **[nanoclaw](https://github.com/qwibitai/nanoclaw)** — same philosophy of giving AI full PC access, with the missing piece: **a structured agile feedback loop so the agent actually improves your results over time.**

---

## Why AgileClaw?

There are three tiers of AI agent tools:

- 🏢 **Full platforms** (OpenClaw, nanoclaw) — powerful, but broad-purpose and complex to self-host
- 🔬 **Research frameworks** (AutoGen, CrewAI, LangChain) — built for multi-agent research, not daily personal use
- 🦅 **AgileClaw** — opinionated, goal-driven, small enough to read in an afternoon

| Feature | AgileClaw | OpenClaw | nanoclaw | AutoGen | LangChain |
|---------|:---------:|:--------:|:--------:|:-------:|:---------:|
| Built-in agile loop | ✅ | ❌ | ❌ | ❌ | ❌ |
| Auto Agile Team per goal | ✅ | ❌ | ❌ | ❌ | ❌ |
| Daily / weekly KPI reports | ✅ | ❌ | ❌ | ❌ | ❌ |
| Full PC access (no sandbox) | ✅ | ✅ | ✅ | ✅ | ❌ |
| < 500 lines of core code | ✅ | ❌ | ✅ | ❌ | ❌ |
| Telegram native | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cron scheduler built-in | ✅ | ✅ | ❌ | ❌ | ❌ |
| File-based memory (no DB) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Skill plugin system | ✅ | ✅ | ❌ | ❌ | ❌ |
| Hot-reload tools & skills | ✅ | ❌ | ❌ | ❌ | ❌ |

**vs OpenClaw:** OpenClaw is a full-featured platform with GUI, extensions, and marketplace. AgileClaw is a tiny hackable core you can read, fork, and own completely.

**vs nanoclaw:** nanoclaw is a minimal agent scaffold. AgileClaw keeps the same simplicity but adds the agile loop, goal teams, cron scheduling, and KPI tracking on top.

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
  max_tool_rounds: 10               # Max tool calls per response
  max_retries: 2

memory:
  dir: "./memory"

skills:
  dir: "./skills"

cron:
  jobs_file: "./cron_jobs.json"

browser:
  headless: false  # Set true for server environments
```

### 3. Set Your Goals

Edit `memory/goals.md`:

```markdown
# My Goals

## KPIs
| Metric          | Current | Target | How to Measure               |
|-----------------|---------|--------|------------------------------|
| Twitter followers | 2,100 | 5,000  | scripts/twitter_followers.py |
| MRR             | $800    | $3,000 | check Stripe dashboard       |
| Daily users     | 150     | 500    | analytics API                |
```

### 4. Run

```bash
python main.py
```

---

## 🔄 How It Works

### Automatic Agile Teams

Every goal request automatically gets its own Agile Team:

```
User: "Grow my app downloads to 10,000 this month"
         ↓
AgileClaw detects goal keywords
         ↓
Creates memory/teams/team-grow-app-downloads-xxxx.md
(charter with KPI definitions, sprint plan, measurement method)
         ↓
Executes with tools, measures results, reports progress
```

### The Agile Loop

```
┌─────────────────────────────────────────────────────────┐
│                    AGILE LOOP                           │
│                                                         │
│  📋 GOAL           🏗  TEAM            🔍 MEASURE        │
│  goals.md    →   auto-create    →    use tools          │
│  KPI targets     charter file        shell/web/api       │
│       │                                    │            │
│       └────────────────────────────────────┘            │
│                         ↓                               │
│  🚀 IMPROVE          📊 REPORT                          │
│  suggest top 3   ←   daily/weekly                       │
│  next actions        KPI summary                        │
└─────────────────────────────────────────────────────────┘
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/agile` | Run full agile review (KPIs vs targets) |
| `/daily` | Daily KPI progress report |
| `/weekly` | Weekly retrospective report |
| `/teams` | List all active agile teams |
| `/skills` | List available skills |
| `/cron` | Show scheduled jobs |
| Just chat | Talk to the agent naturally |

---

## 🏗 Architecture

```
agileclaw/
├── main.py                  # Entry point (< 80 lines)
├── config.example.yaml      # Config template
├── core/
│   ├── agent.py             # Agent brain: chat, agile review, team management
│   ├── claude.py            # Claude API client (tool_use loop, retry, rate limit)
│   ├── memory.py            # File-based memory + Agile Team registry
│   └── skills.py            # Skill catalog (hot-reload)
├── channels/
│   └── telegram.py          # Telegram bot (commands + free chat)
├── tools/
│   ├── __init__.py          # Auto-discovery: loads all tools in this folder
│   ├── shell.py             # Run shell commands
│   ├── files.py             # Read/write files
│   ├── web.py               # Fetch web pages
│   ├── browser.py           # Browser control (Playwright)
│   ├── kpi.py               # KPI upsert / measurement logging
│   ├── threads.py           # Threads API (followers, posts)
│   └── reddit.py            # Reddit API (karma, posts)
├── scheduler/
│   └── cron.py              # Cron job scheduler (APScheduler)
├── agile/
│   ├── loop.py              # Agile system prompts + review builder
│   ├── team.py              # Team charter creation, slugify, goal key
│   └── report.py            # Daily/weekly report prompt builders
├── skills/
│   ├── kpi-daily-check/     # Built-in skill: daily KPI check
│   └── agile-weekly-review/ # Built-in skill: weekly retrospective
└── tests/                   # Unit tests
```

**Core code is tiny:** `core/` + `agile/` is under 600 lines total. Read it in 20 minutes.

---

## 🛠 Tools Available

| Tool | Description |
|------|-------------|
| `shell` | Run any shell command (scripts, CLIs, APIs) |
| `read_file` | Read any file on your machine |
| `write_file` | Write/update any file |
| `web_fetch` | Fetch a URL, extract readable content |
| `browser_open` | Open URL in Playwright browser |
| `browser_click` | Click a page element |
| `browser_type` | Type into input field |
| `browser_get_text` | Extract text from current page |
| `browser_screenshot` | Take a screenshot |
| `kpi_upsert_metric` | Register a KPI metric definition |
| `kpi_log_measurement` | Log a KPI measurement |
| `kpi_list_metrics` | List all KPI metrics |
| `threads_get_followers` | Get Threads follower count |
| `reddit_get_karma` | Get Reddit karma |

### Adding Custom Tools

1. Create `tools/mytool.py` with a `TOOL_DEFINITION` dict and a `run(input, ctx)` function
2. Drop it in the `tools/` folder — it's **auto-discovered on startup** (and hot-reloaded on each request)

No registration needed. That's it.

---

## 🎯 Skills

Skills are reusable agent behaviors defined in plain Markdown. Drop a `SKILL.md` into `skills/your-skill/` and the agent will load and follow it automatically.

```markdown
# skills/my-skill/SKILL.md
## What this skill does
Check my Stripe MRR daily and compare vs target.

## Steps
1. Run `python scripts/stripe_mrr.py`
2. Compare result vs goals.md MRR target
3. If gap > 20%, suggest top 3 actions
```

Built-in skills:
- `kpi-daily-check` — Morning KPI snapshot
- `agile-weekly-review` — Friday retrospective

---

## 💡 Use Cases

**📱 App maker tracking installs**
> "Grow my app downloads to 10,000 by end of March"
→ Creates a team, measures App Store stats daily, suggests what to post/fix

**📝 Content creator tracking engagement**
> "Reach 5,000 Threads followers this sprint"
→ Tracks Threads API followers daily, recommends content strategy adjustments

**💰 SaaS founder tracking MRR**
> "Increase MRR from $800 to $3,000 in Q2"
→ Pulls Stripe data, tracks churn vs target, daily standup report

**📚 Course creator tracking students**
> "Get 500 new course enrollments this month"
→ Checks LMS API, correlates with content calendar, weekly retrospective

---

## 🗺 Roadmap

- [x] Core Claude agent loop with tool_use
- [x] Telegram channel (commands + free chat)
- [x] Cron scheduler
- [x] Agile review loop
- [x] Auto Agile Team creation per goal
- [x] Daily / weekly report builders
- [x] File-based memory + team registry
- [x] Skill plugin system (hot-reload)
- [x] KPI tool (upsert, log, list)
- [x] Threads & Reddit API tools
- [x] Auto tool discovery
- [ ] Discord channel support
- [ ] Web dashboard for KPI visualization
- [ ] Pre-built skill packs (App Store, Stripe, GitHub)
- [ ] Multi-agent delegation (spawn sub-agents per team)
- [ ] OpenClaw integration mode

---

## 🤝 Contributing

AgileClaw is intentionally small. Before adding features, ask:
> *"Can this be a custom tool or skill instead?"*

1. Fork it
2. Make your change (keep it small)
3. Open a PR

**Great first contributions:**
- New tool: `tools/slack.py`, `tools/notion.py`, `tools/stripe.py`
- New channel: `channels/discord.py`
- Example skill in `skills/`
- Bug fixes & tests

---

## 📜 License

MIT — do whatever you want with it.

---

<div align="center">

*Built on the shoulders of [OpenClaw](https://github.com/openclaw/openclaw) and [nanoclaw](https://github.com/qwibitai/nanoclaw).*
*If you find this useful, consider starring ⭐ the repo.*

</div>
